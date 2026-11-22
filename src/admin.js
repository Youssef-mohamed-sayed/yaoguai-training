import { api } from './auth.js';

const esc = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const stat = (label, value) => `<div class="admin-stat"><span>${esc(label)}</span><strong>${Number(value || 0).toLocaleString('en-US')}</strong></div>`;

export async function mountAdmin(root, getUser) {
  root.innerHTML = '<div class="admin-page"><p class="admin-empty">Loading administration data</p></div>';
  try {
    const [summary, members, levels, groups, tasks, submissions, platforms] = await Promise.all([
      api('/admin/overview'), api('/admin/members'), api('/admin/levels'), api('/admin/groups'),
      api('/admin/tasks'), api('/admin/submissions'), api('/platforms'),
    ]);
    render(summary, members, levels, groups, tasks, submissions, platforms);
  } catch (error) {
    if (error.message.includes('Sign in')) {
      root.innerHTML = '<div class="admin-page"><div class="admin-alert">Sign in with an administrator account to open this page</div></div>';
      return;
    }
    root.innerHTML = `<div class="admin-page"><div class="admin-alert error">${esc(error.message)}</div></div>`;
  }

  function render(summary, members, levels, groups, tasks, submissions, platforms) {
    const memberRows = members.map((member) => `<tr><td><strong>${esc(member.username)}</strong><br><span class="muted">${esc(member.email)}</span></td><td><select data-member-level="${esc(member.id)}"><option value="">No level</option>${levels.map((level) => `<option value="${esc(level.id)}" ${member.level?.id === level.id ? 'selected' : ''}>${esc(level.name)}</option>`).join('')}</select></td><td>${member.is_active ? 'Active' : 'Inactive'}</td></tr>`).join('');
    const groupRows = groups.map((group) => `<div class="admin-list-row"><span>${esc(group.name)}</span><span>${group.member_count} members</span></div>`).join('');
    const groupOptions = groups.map((group) => `<option value="${esc(group.id)}">${esc(group.name)}</option>`).join('');
    const memberOptions = members.map((member) => `<option value="${esc(member.id)}">${esc(member.username)}</option>`).join('');
    const platformOptions = platforms.map((platform) => `<option value="${esc(platform.id)}">${esc(platform.name)}</option>`).join('');
    const taskRows = tasks.map((task) => `<div class="admin-list-row"><span>${esc(task.title)}</span><span>${task.deadline_at ? new Date(task.deadline_at).toLocaleDateString() : 'No deadline'}</span></div>`).join('');
    const submissionRows = submissions.map((item) => `<div class="admin-list-row"><span><strong>${esc(item.username)}</strong><br>${esc(item.task_title)} · ${esc(item.status)}</span><span><button class="button button-small" data-review="${esc(item.id)}" data-status="approved">Approve</button> <button class="button button-small" data-review="${esc(item.id)}" data-status="rejected">Return</button></span></div>`).join('');
    root.innerHTML = `<div class="admin-page">
      <header class="admin-heading"><div><p class="section-kicker">Yaoguai Training</p><h1>Administration</h1></div><span class="muted">Signed in as ${esc(getUser()?.username || 'administrator')}</span></header>
      <div class="admin-stats">${stat('Members', summary.members)}${stat('Active today', summary.active_today)}${stat('Groups', summary.groups)}${stat('Modules completed', summary.completed_modules)}</div>
      <div class="admin-columns"><div class="admin-column">
        <section class="admin-panel"><h2>Members</h2><input class="admin-search" id="member-search" type="search" placeholder="Search by username or email" aria-label="Search members"><table class="admin-table"><thead><tr><th>Member</th><th>Level</th><th>Status</th></tr></thead><tbody id="member-rows">${memberRows || '<tr><td colspan="3" class="admin-empty">No members yet</td></tr>'}</tbody></table></section>
        <section class="admin-panel"><h2>Groups</h2><div class="admin-list">${groupRows || '<p class="admin-empty">No groups yet</p>'}</div><form class="admin-form" id="group-form"><label>Group name<input name="name" maxlength="120" required></label><label>Description<input name="description" maxlength="500"></label><label>Platform<select name="platform_id"><option value="">No platform</option>${platformOptions}</select></label><label>Level<select name="level_id"><option value="">No level</option>${levels.map((level) => `<option value="${esc(level.id)}">${esc(level.name)}</option>`).join('')}</select></label><button class="button button-primary" type="submit">Create group</button></form>
        <form class="admin-form" id="member-group-form"><label>Member<select name="user_id" required>${memberOptions}</select></label><label>Group<select name="group_id" required>${groupOptions}</select></label><button class="button" type="submit">Add member to group</button></form></section>
        <section class="admin-panel"><h2>Member levels</h2><div class="admin-list">${levels.map((level) => `<div class="admin-list-row"><span>${esc(level.name)}</span><span>Rank ${level.rank}</span></div>`).join('') || '<p class="admin-empty">No levels configured</p>'}</div><form class="admin-form" id="level-form"><label>Level name<input name="name" maxlength="80" required></label><label>Description<input name="description" maxlength="500"></label><label>Rank<input name="rank" type="number" value="0"></label><button class="button" type="submit">Add level</button></form></section>
      </div><div class="admin-column">
        <section class="admin-panel"><h2>Assign a task</h2><form class="admin-form" id="task-form"><label>Title<input name="title" maxlength="200" required></label><label>Instructions<textarea name="instructions" maxlength="10000"></textarea></label><label>Platform<select name="platform_id" id="task-platform"><option value="">Choose platform</option>${platformOptions}</select></label><label>Module<select name="module_id" id="task-module" required><option value="">Choose module</option></select></label><label>Activities<select name="activity_ids" id="task-activities" multiple size="5" aria-label="Required activities"></select></label><label class="check-label"><input name="requires_review" type="checkbox"> Require administrator review</label><label>Assign to group<select name="group_id"><option value="">Choose group</option>${groupOptions}</select></label><label>Or assign to member<select name="user_id"><option value="">Choose member</option>${memberOptions}</select></label><label>Deadline<input name="deadline_at" type="datetime-local"></label><button class="button button-primary" type="submit">Create assignment</button><p class="form-message" id="task-message" role="status"></p></form><div class="admin-list">${taskRows || '<p class="admin-empty">No tasks assigned</p>'}</div></section>
        <section class="admin-panel"><h2>Submissions to review</h2><div class="admin-list">${submissionRows || '<p class="admin-empty">No submissions</p>'}</div></section>
      </div></div></div>`;

    root.querySelector('#member-search').addEventListener('input', debounce(async (event) => {
      const q = event.target.value;
      const rows = await api(`/admin/members?q=${encodeURIComponent(q)}`);
      root.querySelector('#member-rows').innerHTML = rows.map((member) => `<tr><td><strong>${esc(member.username)}</strong><br><span class="muted">${esc(member.email)}</span></td><td><select data-member-level="${esc(member.id)}"><option value="">No level</option>${levels.map((level) => `<option value="${esc(level.id)}" ${member.level?.id === level.id ? 'selected' : ''}>${esc(level.name)}</option>`).join('')}</select></td><td>${member.is_active ? 'Active' : 'Inactive'}</td></tr>`).join('') || '<tr><td colspan="3" class="admin-empty">No members found</td></tr>';
    }, 250));
    root.querySelector('#member-rows').addEventListener('change', async (event) => {
      const select = event.target.closest('[data-member-level]');
      if (select) await api(`/admin/members/${select.dataset.memberLevel}`, { method: 'PATCH', body: JSON.stringify({ level_id: select.value || null }) });
    });
    root.querySelector('#group-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = new FormData(event.currentTarget);
      await api('/admin/groups', { method: 'POST', body: JSON.stringify(Object.fromEntries(data)) });
      location.reload();
    });
    root.querySelector('#member-group-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = new FormData(event.currentTarget);
      await api(`/admin/groups/${data.get('group_id')}/members/${data.get('user_id')}`, { method: 'PUT', body: JSON.stringify({}) });
      location.reload();
    });
    root.querySelector('#level-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(event.currentTarget));
      data.rank = Number(data.rank);
      await api('/admin/levels', { method: 'POST', body: JSON.stringify(data) });
      location.reload();
    });
    root.querySelector('#task-platform').addEventListener('change', async (event) => {
      const modules = await api(`/platforms/${encodeURIComponent(event.target.value)}/modules`);
      root.querySelector('#task-module').innerHTML = '<option value="">Choose module</option>' + modules.map((module) => `<option value="${esc(module.id)}">${esc(module.title)}</option>`).join('');
      root.querySelector('#task-activities').innerHTML = '';
    });
    root.querySelector('#task-module').addEventListener('change', async (event) => {
      if (!event.target.value) return;
      const module = await api(`/modules/${encodeURIComponent(event.target.value)}`);
      root.querySelector('#task-activities').innerHTML = module.activities.map((activity) => `<option value="${esc(activity.id)}">${esc(activity.title)} · ${esc(activity.type)}</option>`).join('');
    });
    root.querySelector('#task-form').addEventListener('submit', async (event) => {
      event.preventDefault();
      const formData = new FormData(event.currentTarget);
      const activitySelect = root.querySelector('#task-activities');
      const deadline = formData.get('deadline_at');
      const payload = {
        title: formData.get('title'), instructions: formData.get('instructions'),
        platform_id: formData.get('platform_id'), module_id: formData.get('module_id'),
        group_ids: formData.get('group_id') ? [formData.get('group_id')] : [],
        user_ids: formData.get('user_id') ? [formData.get('user_id')] : [],
        deadline_at: deadline ? new Date(deadline).toISOString() : null,
        requirements: [...activitySelect.selectedOptions].map((option) => ({ activity_id: option.value, requires_review: formData.has('requires_review') })),
      };
      try {
        const result = await api('/admin/tasks', { method: 'POST', body: JSON.stringify(payload) });
        root.querySelector('#task-message').textContent = `Assignment created for ${result.assignment_count} target${result.assignment_count === 1 ? '' : 's'}`;
        location.reload();
      } catch (error) {
        root.querySelector('#task-message').textContent = error.message;
      }
    });
    root.querySelectorAll('[data-review]').forEach((button) => button.addEventListener('click', async () => {
      await api(`/admin/submissions/${button.dataset.review}`, { method: 'PATCH', body: JSON.stringify({ status: button.dataset.status, feedback: '' }) });
      location.reload();
    }));
  }
}

function debounce(fn, delay) {
  let timer;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), delay);
  };
}
