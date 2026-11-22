# Lab: Filesystem, Users, and Permissions


## Lab objectives
Build a small shared workspace and prove that permissions behave as expected.

## Safety and prerequisites
Use a disposable Ubuntu/Debian or Fedora VM with administrator access. Take a VM snapshot first. Do not perform account-management tasks on a production machine.

## Tasks
1. Create `/srv/yaoguai-lab` and a group named `labteam`.
2. Create two test users, `labalice` and `labbob`, with home directories.
3. Add both users to `labteam`.
4. Make the workspace owned by root and group-owned by `labteam`.
5. Set the directory to group-shared access with SGID so new entries inherit the group.
6. Create a private file accessible only to its owner.
7. Verify ownership, group membership, and modes using `id`, `getent`, `ls -l`, and `stat`.
8. Document the expected access for owner, group, and other.

## Suggested commands
```bash
sudo groupadd labteam
sudo useradd -m labalice
sudo useradd -m labbob
sudo usermod -aG labteam labalice
sudo usermod -aG labteam labbob
sudo mkdir -p /srv/yaoguai-lab
sudo chown root:labteam /srv/yaoguai-lab
sudo chmod 2770 /srv/yaoguai-lab
sudo -u labalice touch /srv/yaoguai-lab/alice.txt
ls -ld /srv/yaoguai-lab
ls -l /srv/yaoguai-lab
```
Group membership changes may require a new login session. The `2` in `2770` sets SGID on the directory; `770` grants owner and group full access and denies others.

## Validation questions
- Which group owns `alice.txt`?
- Can an unrelated user list the directory?
- Why does the directory have an `s` in its group-execute position?
- What is the risk of setting the directory to `777`?

## Cleanup
Only after confirming the names are the disposable lab accounts:
```bash
sudo userdel -r labalice
sudo userdel -r labbob
sudo groupdel labteam
sudo rm -r -- /srv/yaoguai-lab
```
Verify the exact path before cleanup. Never paste cleanup commands into a real system without checking every target.

## Deliverable
A short report containing commands used, permission interpretation, validation results, and cleanup confirmation.
