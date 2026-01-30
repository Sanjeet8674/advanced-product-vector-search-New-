@echo off
echo Initializing Git repository...
git init

echo Configuring Git user...
git config user.email "sanjeet@example.com"
git config user.name "Sanjeet"

echo Adding .gitignore...
git add .gitignore
git commit -m "Add gitignore"

echo Adding scripts...
git add scripts/generate_products.py
git commit -m "Add product generation script"
git add scripts/embed_products.py
git commit -m "Add embedding script"
git add scripts/run_local_demo.py
git commit -m "Add local demo script"

echo Adding Lambda...
git add lambda/
git commit -m "Add Lambda function and Dockerfile"

echo Adding SQL...
git add sql/
git commit -m "Add SQL schema"

echo Adding Terraform...
git add terraform/
git commit -m "Add Terraform configuration"

echo Adding Project Files...
git add README.md requirements.txt LICENSE run_project.bat
git commit -m "Add documentation and config"

echo Git repository setup complete.
echo now create a new repository on GitHub and run:
echo git remote add origin <YOUR_REPO_URL>
echo git branch -M main
echo git push -u origin main
pause
