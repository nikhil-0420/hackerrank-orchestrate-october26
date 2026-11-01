Agent Trace Staging Directory for HackerRank Orchestrate (October 2026)
Challenge: Ghost Data Still Exists

INSTRUCTIONS FOR SUBMITTING AGENT TRACES:

1. Antigravity IDE Sessions:
   Before copying, close/finish the Antigravity session so log files flush completely to disk.
   Copy the following challenge conversation folder(s) from your Antigravity IDE brain directory:
     Source:
       C:\Users\ACER.DESKTOP-R4G9UL6\.gemini\antigravity-ide\brain\6fe440aa-de21-4a90-851a-5e396defbf40
       (Optional initial clone setup: C:\Users\ACER.DESKTOP-R4G9UL6\.gemini\antigravity-ide\brain\bbf93678-76d7-4708-9a61-117ea9e9753c)
     Destination:
       agent-trace\antigravity\6fe440aa-de21-4a90-851a-5e396defbf40

   CRITICAL SECURITY NOTICE:
   - Do NOT copy anything outside this challenge.
   - Do NOT copy entire ~/.gemini or authentication/credential files.
   - Never include .env files, API keys, or private settings.

2. Claude Chat Export (if applicable):
   If you interacted with Claude via the Claude web or desktop interface:
   - Navigate to: Settings > Privacy > Export data
   - Download the export and extract the conversation export JSON/Markdown file.
   - Place the relevant file(s) into:
       agent-trace\claude\

3. Create the Submission ZIP:
   Run the following PowerShell command from the repository root:
     Compress-Archive -Path .\agent-trace -DestinationPath .\agent-trace.zip -Force
