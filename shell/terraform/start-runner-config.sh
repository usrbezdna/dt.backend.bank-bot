#/bin/bash

echo -e "\e[1;34mStarting RunnerVM configuration...\e[0m"

echo -e "\e[1;34mUpdating packages...\e[0m"
sudo apt upgrade && sudo apt update

# Docker Installation
echo -e "\e[1;34mInstalling Docker...\e[0m"

sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable" -y

sudo apt update
sudo apt install docker-ce -y

echo -e "\e[1;32mDocker Installed!\e[0m"


# Gitlab Runner Installation
echo -e "\e[1;34mInstalling Gitlab Runner...\e[0m"

curl -L "https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.deb.sh" | sudo bash
sudo apt-get install gitlab-runner -y

echo -e "\e[1;32mRunner successfully installed!\e[0m"


# Gitlab Runner Registration
echo -e "\e[1;34mRunning runner registration...\e[0m"

export $(egrep -v '^#' .env.runner | xargs)

sudo gitlab-runner register --non-interactive \
    --url https://gitlab.com/ \
    --registration-token $REGISTRATION_TOKEN \
    --name 'test-runner' \
    --executor "docker" \
    --docker-image "docker:stable" \
    --docker-privileged

echo -e "\e[1;32mRunner was registered!\e[0m"