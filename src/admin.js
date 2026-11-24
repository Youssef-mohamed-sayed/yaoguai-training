import { api } from './auth.js';

const esc = (value = '') => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);
const stat = (label, value) => `<div class="admin-stat"><span>${esc(label)}</span><strong>${Number(value || 0).toLocaleString('en-US')}</strong></div>`;
const dateTime = value => value ? new Date(value).toLocaleString() : 'No deadline';

function memberRows(members, levels) {
  return members.map(member => `<tr>
    <td><button class="admin-member-link" type="button" data-member-detail="${esc(member.id)}">${esc(member.username)}</button><br><span class="muted">${esc(member.email)}</span></td>
    <td><select data-member-level="${esc(member.id)}"><option value="">No level</option>${levels.map(level => `<option value="${esc(level.id)}" ${member.level?.id === level.id ? 'selected' : ''}>${esc(level.name)}</option>`).join('')}</select></td>
    <td>${member.is_active ? 'Active' : 'Inactive'}</td>
  </tr>`).join('');
}

function memberDetailView(detail) {
  const platforms = [...new Set(detail.progress.map(item => item.platform))];
  const progress = platforms.map(platform => {
    const modules = detail.progress.filter(item => item.platform === platform);
    const name = { network: 'Network', linux: 'Linux', programming: 'Programming', crypto: 'Crypto' }[platform] || platform;
    return `<section class="member-progress-platform"><h4>${esc(name)}</h4>${modules.map(module => {
      const pct = module.required_count ? Math.round(module.completed_count / module.required_count * 100) : 0;
      return `<details class="member-progress-module"><summary><span>${esc(module.title)}</span><b>${module.completed_count} of ${module.required_count} · ${pct}%</b></summary><div class="member-progress-track"><i style="width:${pct}%"></i></div><ul>${module.activities.map(activity => `<li><span>${esc(activity.title)}</span><span>${activity.completed ? 'Complete' : activity.started ? 'Started' : 'Not started'}</span></li>`).join('')}</ul></details>`;
    }).join('')}</section>`;
  }).join('');
  const tasks = detail.tasks.map(task => `<article class="member-task"><div><strong>${esc(task.title)}</strong><p>${esc(task.instructions || task.description || '')}</p></div><div><b>${esc(task.status.replace('_', ' '))}</b><span>Due ${esc(dateTime(task.deadline_at))}</span><small>${task.completed_count}/${task.required_count} required activities</small></div></article>`).join('');
  return `<div class="member-detail-heading"><div><p class="section-kicker">MEMBER RECORD</p><h3>${esc(detail.member.username)}</h3><span class="muted">${esc(detail.member.email)}</span></div><span>${detail.member.is_active ? 'Active' : 'Inactive'}</span></div>
    <div class="member-progress-grid">${progress || '<p class="admin-empty">No course progress is available yet.</p>'}</div>
    <h4 class="member-detail-subhead">Assigned tasks</h4><div class="member-task-list">${tasks || '<p class="admin-empty">No tasks assigned to this member.</p>'}</div>`;
}

export async function mountAdmin(root, getUser) {
  try {
    const data = await api('/admin/dashboard');
    const { overview: summary, members, levels, groups, tasks, submissions, platforms } = data;
    render(summary, members, levels, groups, tasks, submissions, platforms);
  } catch (error) {
    root.innerHTML = `<div class="admin-page"><header class="admin-heading"><div><p class="section-kicker">Yaoguai Training</p><h1>Administration</h1></div><span class="muted">${esc(getUser()?.username || 'administrator')}</span></header><div class="admin-alert error" role="alert">Dashboard data could not be loaded: ${esc(error.message)}</div><button class="button" id="admin-retry">Try again</button></div>`;
    root.querySelector('#admin-retry').addEventListener('click', () => { root.innerHTML = '<p class="admin-empty">Loading administration data</p>'; mountAdmin(root, getUser); });
  }

  function render(summary, members, levels, groups, tasks, submissions, platforms) {
    const memberMarkup = memberRows(members, levels);
    const groupMarkup = groups.map(group => `<details class="admin-group"><summary><span><strong>${esc(group.name)}</strong><small>${group.member_count} members</small></span><span>${esc(group.description || '')}</span></summary><div class="admin-group-members">${group.members.map(member => `<span>${esc(member.username)} <small>${esc(member.email)}</small><button type="button" class="button button-small" data-remove-member="${esc(member.id)}" data-group-id="${esc(group.id)}" aria-label="Remove ${esc(member.username)} from ${esc(group.name)}">Remove</button></span>`).join('') || '<p class="admin-empty">This list has no members yet.</p>'}</div></details>`).join('');
    const groupOptions = groups.map(group => `<option value="${esc(group.id)}">${esc(group.name)} (${group.member_count})</option>`).join('');
    const memberOptions = members.map(member => `<option value="${esc(member.id)}">${esc(member.username)} · ${esc(member.email)}</option>`).join('');
    const platformOptions = platforms.map(platform => `<option value="${esc(platform.id)}">${esc(platform.name)}</option>`).join('');
    const taskRows = tasks.map(task => `<article class="admin-list-row admin-task-row"><span><strong>${esc(task.title)}</strong><small>${task.targets.map(target => `${target.type === 'group' ? 'List' : 'User'}: ${esc(target.name)}`).join(' · ') || 'No recipients'} · ${task.assignments} assignment${task.assignments === 1 ? '' : 's'}</small></span><span>${task.deadline_at ? `Due ${esc(dateTime(task.deadline_at))}` : 'No deadline'}<small>${task.active ? 'Active' : 'Inactive'}</small></span></article>`).join('');
    const submissionRows = submissions.map(item => `<div class="admin-list-row"><span><strong>${esc(item.username)}</strong><br>${esc(item.task_title)} · ${esc(item.status)}</span><span><button class="button button-small" data-review="${esc(item.id)}" data-status="approved">Approve</button> <button class="button button-small" data-review="${esc(item.id)}" data-status="rejected">Return</button></span></div>`).join('');
    root.innerHTML = `<div class="admin-page">
      <header class="admin-heading"><div><p class="section-kicker">Yaoguai Training</p><h1>Administration</h1></div><span class="muted">Signed in as ${esc(getUser()?.username || 'administrator')}</span></header>
      <div class="admin-stats">${stat('Members', summary.members)}${stat('Active today', summary.active_today)}${stat('Groups', summary.groups)}${stat('Modules completed', summary.completed_modules)}</div>
      <div class="admin-columns"><div class="admin-column">
        <section class="admin-panel"><h2>Members</h2><p class="admin-section-note">Select a member to inspect course progress and assigned work.</p><input class="admin-search" id="member-search" type="search" placeholder="Search by username or email" aria-label="Search members"><div class="table-scroll"><table class="admin-table"><thead><tr><th>Member</th><th>Level</th><th>Status</th></tr></thead><tbody id="member-rows">${memberMarkup || '<tr><td colspan="3" class="admin-empty">No members yet</td></tr>'}</tbody></table></div><div class="admin-member-detail" id="member-detail" aria-live="polite"><p class="admin-empty">Choose a member to view their progress.</p></div></section>
        <section class="admin-panel"><h2>User lists</h2><div class="admin-list">${groupMarkup || '<p class="admin-empty">No lists yet. Create a list to group learners for assignments.</p>'}</div><form class="admin-form" id="group-form"><label>List name<input name="name" maxlength="120" required></label><label>Description<input name="description" maxlength="500"></label><label>Course focus<select name="platform_id"><option value="">All courses</option>${platformOptions}</select></label><button class="button button-primary" type="submit">Create user list</button></form><form class="admin-form" id="member-group-form"><label>List<select name="group_id" required><option value="">Choose a list</option>${groupOptions}</select></label><label>Members<select name="user_ids" multiple size="5" required aria-label="Members to add">${memberOptions}</select><small>Use Ctrl or Command to select multiple members.</small></label><button class="button" type="submit">Add members to list</button><p class="form-message" id="group-message" role="status"></p></form></section>
        <section class="admin-panel"><h2>Member levels</h2><div class="admin-list">${levels.map(level => `<div class="admin-list-row"><span>${esc(level.name)}</span><span>Rank ${level.rank}</span></div>`).join('') || '<p class="admin-empty">No levels configured</p>'}</div><form class="admin-form" id="level-form"><label>Level name<input name="name" maxlength="80" required></label><label>Description<input name="description" maxlength="500"></label><label>Rank<input name="rank" type="number" value="0"></label><button class="button" type="submit">Add level</button></form></section>
      </div><div class="admin-column">
        <section class="admin-panel"><h2>Assign work</h2><form class="admin-form" id="task-form"><label>Task title<input name="title" maxlength="200" required></label><label>Instructions<textarea name="instructions" maxlength="10000"></textarea></label><label>Course<select name="platform_id" id="task-platform" required><option value="">Choose course</option>${platformOptions}</select></label><label>Module<select name="module_id" id="task-module" required><option value="">Choose module</option></select></label><label>Required activities<select name="activity_ids" id="task-activities" multiple size="5" aria-label="Required activities" required></select></label><label class="check-label"><input name="requires_review" type="checkbox"> Require administrator review</label><label>Assign to lists<select name="group_ids" multiple size="4" aria-label="Lists to assign"></select><small>Leave empty if assigning directly to selected members.</small></label><label>Assign directly to members<select name="user_ids" multiple size="5" aria-label="Members to assign">${memberOptions}</select></label><label>Deadline<input name="deadline_at" type="datetime-local"></label><button class="button button-primary" type="submit">Assign task</button><p class="form-message" id="task-message" role="status"></p></form><div class="admin-list">${taskRows || '<p class="admin-empty">No assigned tasks yet</p>'}</div></section>
        <section class="admin-panel"><h2>Submissions to review</h2><div class="admin-list">${submissionRows || '<p class="admin-empty">No submissions</p>'}</div></section>
      </div></div></div>`;
    root.querySelector('#task-form [name="group_ids"]').innerHTML = groupOptions;

    const showMember = async id => {
      const panel = root.querySelector('#member-detail');
      panel.innerHTML = '<p class="admin-empty">Loading member progress</p>';
      try { panel.innerHTML = memberDetailView(await api(`/admin/members/${encodeURIComponent(id)}`)); }
      catch (error) { panel.innerHTML = `<p class="admin-alert error">${esc(error.message)}</p>`; }
    };
    root.querySelector('#member-rows').addEventListener('click', event => {
      const button = event.target.closest('[data-member-detail]');
      if (button) showMember(button.dataset.memberDetail);
    });
    root.querySelector('#member-search').addEventListener('input', debounce(async event => {
      try {
        const rows = await api(`/admin/members?q=${encodeURIComponent(event.target.value)}`);
        root.querySelector('#member-rows').innerHTML = memberRows(rows, levels) || '<tr><td colspan="3" class="admin-empty">No members found</td></tr>';
      } catch (error) { root.querySelector('#member-rows').innerHTML = `<tr><td colspan="3" class="admin-alert error">${esc(error.message)}</td></tr>`; }
    }, 250));
    root.querySelector('#member-rows').addEventListener('change', async event => {
      const select = event.target.closest('[data-member-level]');
      if (select) {
        try { await api(`/admin/members/${select.dataset.memberLevel}`, { method: 'PATCH', body: JSON.stringify({ level_id: select.value || null }) }); }
        catch (error) { root.querySelector('#member-detail').innerHTML = `<p class="admin-alert error">${esc(error.message)}</p>`; }
      }
    });
    root.querySelector('#group-form').addEventListener('submit', async event => {
      event.preventDefault();
      try { await api('/admin/groups', { method: 'POST', body: JSON.stringify(Object.fromEntries(new FormData(event.currentTarget))) }); location.reload(); }
      catch (error) { root.querySelector('#group-message').textContent = error.message; }
    });
    root.querySelector('#member-group-form').addEventListener('submit', async event => {
      event.preventDefault();
      const form = new FormData(event.currentTarget), groupId = form.get('group_id'), userIds = form.getAll('user_ids');
      try {
        await Promise.all(userIds.map(userId => api(`/admin/groups/${encodeURIComponent(groupId)}/members/${encodeURIComponent(userId)}`, { method: 'PUT', body: '{}' })));
        location.reload();
      } catch (error) { root.querySelector('#group-message').textContent = error.message; }
    });
    root.querySelectorAll('[data-remove-member]').forEach(button => button.addEventListener('click', async () => {
      try { await api(`/admin/groups/${button.dataset.groupId}/members/${button.dataset.removeMember}`, { method: 'DELETE' }); location.reload(); }
      catch (error) { root.querySelector('#group-message').textContent = error.message; }
    }));
    root.querySelector('#level-form').addEventListener('submit', async event => {
      event.preventDefault();
      const data = Object.fromEntries(new FormData(event.currentTarget)); data.rank = Number(data.rank);
      try { await api('/admin/levels', { method: 'POST', body: JSON.stringify(data) }); location.reload(); }
      catch (error) { root.querySelector('#member-detail').innerHTML = `<p class="admin-alert error">${esc(error.message)}</p>`; }
    });
    root.querySelector('#task-platform').addEventListener('change', async event => {
      const moduleSelect = root.querySelector('#task-module');
      moduleSelect.innerHTML = '<option value="">Choose module</option>';
      root.querySelector('#task-activities').innerHTML = '';
      if (!event.target.value) return;
      try {
        const modules = await api(`/platforms/${encodeURIComponent(event.target.value)}/modules`);
        moduleSelect.innerHTML += modules.map(module => `<option value="${esc(module.id)}">${esc(module.title)}</option>`).join('');
      } catch (error) { root.querySelector('#task-message').textContent = error.message; }
    });
    root.querySelector('#task-module').addEventListener('change', async event => {
      root.querySelector('#task-activities').innerHTML = '';
      if (!event.target.value) return;
      try {
        const module = await api(`/modules/${encodeURIComponent(event.target.value)}`);
        root.querySelector('#task-activities').innerHTML = module.activities.map(activity => `<option value="${esc(activity.id)}">${esc(activity.title)} · ${esc(activity.type)}</option>`).join('');
      } catch (error) { root.querySelector('#task-message').textContent = error.message; }
    });
    root.querySelector('#task-form').addEventListener('submit', async event => {
      event.preventDefault();
      const form = new FormData(event.currentTarget), deadline = form.get('deadline_at');
      const activitySelect = root.querySelector('#task-activities');
      const payload = {
        title: form.get('title'), instructions: form.get('instructions'),
        platform_id: form.get('platform_id'), module_id: form.get('module_id'),
        group_ids: form.getAll('group_ids'), user_ids: form.getAll('user_ids'),
        deadline_at: deadline ? new Date(deadline).toISOString() : null,
        requirements: [...activitySelect.selectedOptions].map(option => ({ activity_id: option.value, requires_review: form.has('requires_review') })),
      };
      try {
        const result = await api('/admin/tasks', { method: 'POST', body: JSON.stringify(payload) });
        root.querySelector('#task-message').textContent = `Assigned to ${result.assignment_count} target${result.assignment_count === 1 ? '' : 's'}.`;
        setTimeout(() => mountAdmin(root, getUser), 600);
      } catch (error) { root.querySelector('#task-message').textContent = error.message; }
    });
    root.querySelectorAll('[data-review]').forEach(button => button.addEventListener('click', async () => {
      try { await api(`/admin/submissions/${button.dataset.review}`, { method: 'PATCH', body: JSON.stringify({ status: button.dataset.status, feedback: '' }) }); location.reload(); }
      catch (error) { root.querySelector('.admin-column:last-child').insertAdjacentHTML('afterbegin', `<p class="admin-alert error">${esc(error.message)}</p>`); }
    }));
  }
}

function debounce(fn, delay) {
  let timer;
  return (...args) => { clearTimeout(timer); timer = setTimeout(() => fn(...args), delay); };
}
