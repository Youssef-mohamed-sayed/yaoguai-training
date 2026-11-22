# Course Coverage and Completion Checklist

This document maps every required learning objective to the exact lesson files that teach it. A checked item means the learner has completed the relevant lessons and practice, not merely opened the file.

- [ ] **Linux basics, distributions, kernel, GNU/Linux, architecture, open source**  
  Coverage: `01-introduction-to-linux/01-what-is-linux.md; 01-introduction-to-linux/02-linux-architecture-and-open-source.md; 02-distributions-and-environments/01-linux-distributions.md`
- [ ] **Desktop environments, shells, Bash, VMs, and WSL**  
  Coverage: `02-distributions-and-environments/02-desktops-shells-vms-and-wsl.md`
- [ ] **Filesystem hierarchy and required directories**  
  Coverage: `03-filesystem-hierarchy/01-filesystem-tree-and-directories.md`
- [ ] **Absolute/relative paths, hidden files, file types, extensions, inodes, hard and symbolic links**  
  Coverage: `03-filesystem-hierarchy/02-paths-hidden-files-types-and-links.md; 04-command-line-fundamentals/02-navigation-and-shell-efficiency.md`
- [ ] **Command-line navigation and efficiency: pwd, ls, cd, tree, history, completion, quoting, globbing, variables, substitution, shortcuts**  
  Coverage: `04-command-line-fundamentals/01-terminal-shell-and-command-syntax.md; 04-command-line-fundamentals/02-navigation-and-shell-efficiency.md`
- [ ] **File operations: mkdir, rmdir, touch, cp, mv, rm, file, stat, ln, cat, less, head, tail, clear, man, which, type**  
  Coverage: `05-files-and-directories/01-create-copy-move-and-remove.md; 05-files-and-directories/02-reading-and-inspecting-files.md; 04-command-line-fundamentals/01-terminal-shell-and-command-syntax.md`
- [ ] **Users, groups, IDs, root, system accounts, passwd/shadow/group/sudoers, account commands**  
  Coverage: `06-users-and-permissions/01-users-groups-and-account-files.md`
- [ ] **Permissions, chmod, chown, chgrp, sudo, su, numeric modes, ownership**  
  Coverage: `06-users-and-permissions/02-permissions-chmod-chown-and-sudo.md`
- [ ] **SUID, SGID, sticky bit, least privilege, privilege awareness**  
  Coverage: `06-users-and-permissions/03-special-permissions-and-least-privilege.md; 13-linux-security-basics/01-least-privilege-and-defensive-administration.md`
- [ ] **Processes, PID/PPID, states, signals, foreground/background, process monitoring and commands**  
  Coverage: `07-processes-and-services/01-processes-signals-and-monitoring.md`
- [ ] **Services, daemons, systemd, systemctl, journalctl, logs**  
  Coverage: `07-processes-and-services/02-services-systemd-and-logs.md`
- [ ] **stdin, stdout, stderr, file descriptors, pipes, redirection, chaining, exit codes**  
  Coverage: `08-text-processing-and-pipelines/01-streams-redirection-and-pipes.md`
- [ ] **grep, sed, awk, cut, sort, uniq, wc, tr, tee, xargs, find, regular expressions, log analysis**  
  Coverage: `08-text-processing-and-pipelines/02-grep-sed-awk-and-log-analysis.md; 10-searching-and-security-inspection/01-find-locate-and-whereis.md`
- [ ] **Package management: apt/dpkg, dnf/rpm, pacman, repositories, dependencies, verification, troubleshooting**  
  Coverage: `09-package-management/01-apt-and-dpkg.md; 09-package-management/02-dnf-rpm-and-pacman.md`
- [ ] **File searching: find, locate, updatedb, whereis, which, grep -R; attribute and permission searches**  
  Coverage: `10-searching-and-security-inspection/01-find-locate-and-whereis.md`
- [ ] **Defensive review of sensitive configuration, credentials, world-writable and SUID files**  
  Coverage: `10-searching-and-security-inspection/02-defensive-filesystem-audit.md; 13-linux-security-basics/01-least-privilege-and-defensive-administration.md`
- [ ] **SSH client/server, ports, keys, host verification, ssh-agent, SCP, SFTP, config, troubleshooting**  
  Coverage: `11-ssh-and-remote-access/01-ssh-client-and-host-verification.md; 11-ssh-and-remote-access/02-ssh-keys-agent-and-file-transfer.md`
- [ ] **Bash scripts, shebang, variables, input, arguments, exit codes, conditionals, case, loops, functions, arrays, arithmetic, strings, tests, debugging, safe handling**  
  Coverage: `12-bash-scripting/01-script-structure-variables-and-input.md; 12-bash-scripting/02-conditionals-loops-functions-and-arrays.md; 12-bash-scripting/03-safe-scripting-debugging-and-error-handling.md`
- [ ] **Complete scripts: system info, file checker, backup, log analyzer, input validator, monitoring**  
  Coverage: `12-bash-scripting/03-safe-scripting-debugging-and-error-handling.md`
- [ ] **Hands-on filesystem, users/permissions, logs, processes/services, SSH, and Bash labs**  
  Coverage: `14-practical-labs/01-lab-filesystem-and-permissions.md; 14-practical-labs/02-lab-authentication-log-analysis.md; 14-practical-labs/03-lab-processes-services-and-ssh.md; 14-practical-labs/04-lab-build-a-log-analyzer.md`
- [ ] **OverTheWire: Bandit connection, level workflow, note-taking, hints, and verified introductory challenges**  
  Coverage: `15-overthewire-bandit/01-bandit-introduction.md; 15-overthewire-bandit/02-bandit-level-0-to-1.md through 15-overthewire-bandit/13-bandit-level-11-to-34-practice-map.md`
- [ ] **Cybersecurity context: pentesting labs, auditing, log analysis, incident response, forensics, network troubleshooting, CTFs, automation**  
  Coverage: `08-text-processing-and-pipelines/02-grep-sed-awk-and-log-analysis.md; 10-searching-and-security-inspection/02-defensive-filesystem-audit.md; 13-linux-security-basics/01-least-privilege-and-defensive-administration.md; 14-practical-labs/`

## Final learner sign-off
- [ ] I can explain the purpose of each command I use.
- [ ] I verify paths and permissions before destructive or privileged operations.
- [ ] I use a regular account for routine work.
- [ ] I can write and debug a small Bash script.
- [ ] I can connect to a lab host using SSH and verify its host identity.
- [ ] I can analyze a sample log and distinguish evidence from assumptions.
- [ ] I have completed the Bandit levels I attempted using the official current instructions.
