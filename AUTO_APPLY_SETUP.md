# Auto-Apply Setup Guide

This automation tool monitors remote job boards and automatically applies to matching job opportunities.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure your preferences in `config.json`:
   - Set `min_salary` for minimum acceptable salary
   - Add your required skills under `required_skills`
   - Specify job types (full-time, contract, etc.)
   - Set preferred locations

## Configuration

### Filters

- **min_salary**: Minimum annual salary in USD
- **max_salary**: Maximum annual salary (null for unlimited)
- **required_skills**: List of tech skills to filter by
- **job_types**: Types of positions (full-time, contract, freelance, etc.)
- **locations**: Preferred work locations (Remote, Anywhere, etc.)
- **exclude_keywords**: Keywords to exclude from results

### Application Settings

- **auto_message**: Enable automatic application messages
- **message_template**: Default cover message for applications
- **max_applications_per_day**: Rate limiting for applications
- **apply_delay_seconds**: Delay between applications (avoid rate limits)

### Monitoring

- **check_interval_minutes**: How often to check for new jobs (default: 60 minutes)
- **log_level**: Logging verbosity (INFO, DEBUG, ERROR)

## Usage

### Run Once (Check for New Jobs)

```bash
python auto-apply.py --check-once
```

### Run Continuously

```bash
python auto-apply.py
```

This will run the automation loop, checking for new jobs at your configured interval.

## Job History

Applied jobs are tracked in `applied_jobs.json` to prevent duplicate applications.

## Supported Job Boards

- **RemoteOK** - Large remote job marketplace

## Extending

To add support for additional job boards:

1. Create a new class inheriting from `JobBoard`
2. Implement `fetch_jobs()` and `apply()` methods
3. Add configuration in `config.json`

Example:

```python
class NewBoardName(JobBoard):
    def __init__(self, config: Dict):
        super().__init__('Board Name', config)
    
    def fetch_jobs(self, filters: Dict) -> List[Dict]:
        # Implement job fetching
        pass
    
    def apply(self, job_id: str) -> bool:
        # Implement application logic
        pass
```

## Notes

- Always review applications before they're submitted
- Respect job board rate limits and terms of service
- Start with `--check-once` mode to verify configuration
- Monitor logs for any errors or issues

## Troubleshooting

**No jobs found:**
- Check that filters aren't too restrictive
- Verify required_skills match actual job postings
- Try lowering min_salary temporarily

**Rate limits exceeded:**
- Increase `apply_delay_seconds`
- Decrease `max_applications_per_day`
- Increase `check_interval_minutes`

**API errors:**
- Check internet connection
- Verify job board APIs are accessible
- Check log files for specific error messages
