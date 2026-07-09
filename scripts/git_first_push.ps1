param(
    [Parameter(Mandatory=$true)][string]$GitHubUser,
    [Parameter(Mandatory=$true)][string]$RepoName
)

git init
git add .
git commit -m "Initial MVP"
git branch -M main
git remote add origin "https://github.com/$GitHubUser/$RepoName.git"
git push -u origin main
Write-Host "Now enable GitHub Pages: Settings > Pages > Source: GitHub Actions"
