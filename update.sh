echo "Updating, please wait"
git stash
git pull origin main
git stash pop
echo "Update done"
