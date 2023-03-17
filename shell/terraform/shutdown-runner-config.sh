
echo -e "\e[1;34mUnregistering Gitlab Runner...\e[0m"
sudo gitlab-runner unregister --url https://gitlab.org/ --name 'test-runner'

echo -e "\e[1;32mOK!\e[0m"