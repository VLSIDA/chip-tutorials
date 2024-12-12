# Git

## UCSC GitLab

We will be using the UCSC GitLab server at:

[https://git.ucsc.edu](https://git.ucsc.edu)

**Note that this is not GitHub!**
We will create a repository for this class for you to submit assignments in.

There is a lot of information provided by UCSC at:

[https://its.ucsc.edu/gitlab/resources.html](https://its.ucsc.edu/gitlab/resources.html)


## Learn git

Git is frequently used in large projects to aid
collaboration among multiple developers by tracking revisions. Git is
installed on our guest Linux image. You should go through the
following git tutorial to learn how to use basic git commands:

[https://gitimmersion.com/](https://gitimmersion.com/)

## Key-based authentication

Once you are familiar with the basics of git, you should generate an
SSH public/private key pair on your computer by doing the
following:

`ssh-keygen`

You can leave the password empty for convenience, or else, you can
type the password each time you do a git command on the remote
server. This will generate two files `~/.ssh/id_rsa` and
`~/.ssh/id_rsa.pub` which are your private and public key,
respectively. These will be used to authenticate to the git server to
clone the repository and push your assignments.

Add your *public key* to your GitLab settings by clicking on your icon in the
upper right and selecting "Preferences". On the left hand side menu,
select "SSH Keys" on the left side as shown here:

![](figs/gitlab_preferences.png)

Paste the public key into the space provided and click ``Add key'' to add it.

More information on ssh is availble at:

[https://docs.gitlab.com/ee/user/ssh.html](https://docs.gitlab.com/ee/user/ssh.html)

## Cloning your repo

You can now clone your personal repository for the class by typing:

`git clone git@git.ucsc.edu:cse122/s23/userid.git newname`

where userid is your UCSC ID and newname is what you want to call the
repository on your local machine. **Note: All students use cse122 above
including those in CSE 222A!** You can now use normal git commands in your
repository. 

If you are new to git, you can (and should!) use the web page to confirm files
in your repository:

[https://git.ucsc.edu/cse122/s23/userid](https://git.ucsc.edu/cse122/s23/userid)

where userid is your UCSC ID.



