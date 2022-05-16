# Contributing to Force of Wind

Thanks for your interest in contributing to Force of Wind!

This document will just cover a few basics of what we would like from contributors.

## How to get started

1. Clone the git repository locally to your PC. See [here](https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository).

2. Follow the setup instructions in [README.md](/README.md) to get it running.

3. Import card data to the database:
`python manage.py importjson`

4. Contact Kossetsu for an API key to obtain the card images on your local machine for development. To attach these images to the imported cards run
`python manage.py assign_existing_card_images`

5. Once you've verified it works locally, you're ready to start contributing!

## How to find something to do

Please check the [Issues Log](https://github.com/Enhaloed/fowsim/issues) for issues that need to be worked on. Feel free to add new issues here if you intend to work on something which is not currently listed (such as something which came out of a discussion on Discord).

## How to make a change

For making code changes, please utilise the following process. For all git operations, it doesn't matter if you use GitHub's desktop app or a terminal - use whichever is easier for you!

1. [Create a new branch](https://docs.github.com/en/issues/tracking-your-work-with-issues/creating-a-branch-for-an-issue) to store your work on. For nice traceability, please name your branch with the number of the issue you're working on and something descriptive: `45-fix-text-too-large` if you were working on issue #45 and fixing an issue with the site where the text was too large, for example.

2. `git commit` your changes to the branch on your PC, then `git push` them to the repo.

3. Make sure to test your changes thoroughly, just in case there were unintended consequences of a change you made.

4. Once you're happy with the changes, [create a pull request](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/creating-a-pull-request) into the `main` branch. Make sure it is linked to the issue and assign [request review](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/proposing-changes-to-your-work-with-pull-requests/requesting-a-pull-request-review) from Enhaloed or Kossetsu or both.

5. After your code has been reviewed, you'll either need to make some changes or it will be good to go! If it's all good you don't need to do anything else - it'll be merged into main and eventually deployed to the live server. Thanks!

## Code Style

We don't follow any specific code style. We just request you keep your code formatting, variable naming and etc similar to the file you're changing to keep consistency. If you have any questions ask us, or we'll check it out in the review anyway.

## How much do I have to do?

Nothing! There is no pressure to continue contributing, so never feel like you're "slacking off" or anything. We're grateful for any contributions you have the time and effort to spare to make.

## I have other questions!

Please contact us on Discord and we'll do our best to help, and then update this document to reflect.