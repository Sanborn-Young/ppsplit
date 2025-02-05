#### User this on any transcripts that are just a long line of text

This is not a sophisticated tool.  It simply allows you to pick a transcript that something like my MP3ToTxt has generated, and apply the smallest of formatting to make it more readable.

It can also be used if you use Live Transcribe app on your phone.  You paste and copy the transcript from your phone to your PC, then use this to parse into something a bit more readable.

#### What Do I Need?

While the script is here, and you could "just run it," I think it is better to set up a virtual environment to run it in.  

```Powershell
# 1. 
# Install pyvenv to manage the virtual environment.
# Most AI will help you do this

# 2. Restart PowerShell session
# Close and reopen PowerShell after pyvenv

# 3. cd to the clone github

# 4. Install Python 3.11.0
pyenv install 3.11.0

# 5. Set as local Python version
pyenv local 3.11.0

# 6. Create virtual environment but see below debugging to get it going
python -m venv ppsplit

# 7. Turn it on

.\ppsplit\Scripts\Activate.ps1


# 8. Check to verify that you are running Python 3.11.0

python --version
```
