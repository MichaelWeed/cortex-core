# Monthly Validation Schedule

## Purpose
Run catalog validation monthly to:
- Detect deprecated models
- Verify tools still work
- Track implementation status
- Maintain catalog accuracy

## Cost
- **Per run**: < $0.01 (100-150 tokens total)
- **Annual**: < $0.12
- Uses minimal test prompts (5 tokens max)

## Quick Run
```bash
./validate_monthly.sh
```

## Automation Options

### macOS (launchd)
Create `~/Library/LaunchAgents/com.cortexcore.validation.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.cortexcore.validation</string>
    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>/path/to/cortex-core/validate_monthly.sh</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Day</key>
        <integer>1</integer>
        <key>Hour</key>
        <integer>2</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.cortexcore.validation.plist
```

### Linux (cron)
```bash
crontab -e
# Add: 0 2 1 * * cd /path/to/cortex-core && ./validate_monthly.sh
```

## Manual Reminder
Set a monthly calendar reminder: "Run cortex-core validation"

