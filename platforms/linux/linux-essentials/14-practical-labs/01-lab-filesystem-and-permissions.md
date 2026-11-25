# Lab: Filesystem, Users, and Permissions


## Lab objectives
Build a small shared workspace and prove, with commands, that ownership and permissions behave exactly as modules 05 and 06 predict.

## Safety and prerequisites
Use a disposable Ubuntu/Debian or Fedora VM where you have administrator access. **Take a VM snapshot before starting.** Do not perform account-management tasks on a production machine, and never on a machine you do not own.

## Scenario
Your team needs a shared directory at `/srv/yaoguai-lab`. Two test users, `labalice` and `labbob`, must both be able to create and edit files there, files created by either must stay in the team group automatically, and nobody else on the system may enter the directory. One file inside must be private to its creator.

## Tasks
1. Create a group named `labteam`.
2. Create two test users, `labalice` and `labbob`, each with a home directory and a login shell.
3. Add both users to `labteam`.
4. Create `/srv/yaoguai-lab`, owned by root and group-owned by `labteam`.
5. Set the directory to mode `2770`: full access for owner and group, nothing for others, with SGID so new entries inherit the group.
6. As `labalice`, create a file in the workspace, then create a second file that only she can read.
7. Verify everything: ownership, group membership, modes, and actual access as the other user.
8. Document the expected access for owner, group, and other on each object.

## Suggested commands
```bash
sudo groupadd labteam
sudo useradd -m -s /bin/bash labalice
sudo useradd -m -s /bin/bash labbob
sudo usermod -aG labteam labalice
sudo usermod -aG labteam labbob
sudo mkdir -p /srv/yaoguai-lab
sudo chown root:labteam /srv/yaoguai-lab
sudo chmod 2770 /srv/yaoguai-lab
sudo -u labalice touch /srv/yaoguai-lab/alice.txt
sudo -u labalice sh -c 'printf "alice only\n" > /srv/yaoguai-lab/alice-private.txt && chmod 600 /srv/yaoguai-lab/alice-private.txt'
ls -ld /srv/yaoguai-lab
ls -l /srv/yaoguai-lab
id labalice
stat /srv/yaoguai-lab/alice.txt
```

Notes on the subtle parts:

- `sudo -u labalice command` runs one command *as* that user, perfect for tests without switching accounts.
- The `2` in `2770` is the SGID bit (module 06 lesson 3); `770` grants owner and group full access and nothing to others.
- Group membership changes apply to new login sessions; `sudo -u` starts a fresh context, which sidesteps that for testing.

## Validation: prove it works
Run each check and compare with the expected answer *before* opening the explanation.

**Check 1.** Which group owns `alice.txt`, and why is it not `labalice`?

<details>
<summary>Show answer</summary>

`labteam`. The directory's SGID bit makes new files inherit the directory's group instead of the creator's primary group. Confirm: `ls -l /srv/yaoguai-lab/alice.txt` shows group `labteam`.
</details>

**Check 2.** Can `labbob` create a file in the workspace? Can an unrelated user (your normal account, if not in `labteam`) even list the directory?

<details>
<summary>Show answer</summary>

```bash
sudo -u labbob touch /srv/yaoguai-lab/bob.txt      # succeeds
sudo -u "$USER" ls /srv/yaoguai-lab                # Permission denied (if you are not in labteam)
```

`bob` is a group member with `rwx` through the group; outsiders get `---`, which denies even listing.
</details>

**Check 3.** Can `labbob` read `alice-private.txt`?

<details>
<summary>Show answer</summary>

No. Mode `600` means owner-only; group membership is irrelevant to a file that grants its group nothing:

```bash
sudo -u labbob cat /srv/yaoguai-lab/alice-private.txt   # Permission denied
```
</details>

**Check 4.** What is the specific risk if someone "fixes" an access complaint here with `chmod 777 /srv/yaoguai-lab`?

<details>
<summary>Show answer</summary>

Every account on the system can now read, create, delete, and rename anything in the workspace, including deleting alice's private file (directory `w+x` controls entry removal). The correct fix for access complaints is always group membership, never world permissions.
</details>

## Cleanup
Only after confirming the names are the disposable lab accounts:

```bash
sudo userdel -r labalice
sudo userdel -r labbob
sudo groupdel labteam
sudo rm -r -- /srv/yaoguai-lab
```

Verify the exact path before the final command, and never paste cleanup commands into a real system without checking every target. Then roll back to your snapshot if you want a pristine VM.

## Deliverable
A short report: the commands used, the `ls -l`/`stat` evidence for each object, the four validation answers in your own words, and confirmation of cleanup.

## Common mistakes
- Forgetting `-a` in `usermod -aG` and wiping memberships.
- Expecting group changes to apply to already-running sessions.
- Setting SGID but forgetting the group has no write bit (`2750` lets the group in but not let it create).
