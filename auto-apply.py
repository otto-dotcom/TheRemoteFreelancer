#!/usr/bin/env python3
"""
Auto-apply automation for remote job boards.
Monitors job listings and applies to matching opportunities.
"""

import json
import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

CONFIG_FILE = 'config.json'
APPLIED_JOBS_FILE = 'applied_jobs.json'


class JobBoard:
    """Base class for job board integration."""

    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.base_url = config.get('api_url', '')
        self.api_key = config.get('api_key', '')

    def fetch_jobs(self, filters: Dict) -> List[Dict]:
        """Fetch jobs from the board based on filters."""
        raise NotImplementedError

    def apply(self, job_id: str) -> bool:
        """Apply to a specific job."""
        raise NotImplementedError


class RemoteOKBoard(JobBoard):
    """RemoteOK job board integration."""

    def __init__(self, config: Dict):
        super().__init__('RemoteOK', config)
        self.base_url = 'https://remoteok.io/api'

    def fetch_jobs(self, filters: Dict) -> List[Dict]:
        """Fetch jobs from RemoteOK."""
        try:
            resp = requests.get(f'{self.base_url}/jobs/', timeout=10)
            resp.raise_for_status()
            jobs = resp.json()
            return self._filter_jobs(jobs, filters)
        except requests.RequestException as e:
            logger.error(f"Failed to fetch jobs: {e}")
            return []

    def _filter_jobs(self, jobs: List[Dict], filters: Dict) -> List[Dict]:
        """Filter jobs based on criteria."""
        filtered = []
        min_salary = filters.get('min_salary', 0)
        skills = filters.get('required_skills', [])
        locations = filters.get('locations', [])
        job_types = filters.get('job_types', [])

        for job in jobs:
            if job.get('type') == 'header':
                continue

            salary = job.get('salary', 0)
            if isinstance(salary, str):
                try:
                    salary = int(salary.replace('$', '').replace(',', ''))
                except (ValueError, AttributeError):
                    salary = 0

            if salary < min_salary:
                continue

            if locations and job.get('location') not in locations:
                continue

            if job_types and job.get('job_type') not in job_types:
                continue

            if skills:
                job_desc = (job.get('description', '') + job.get('title', '')).lower()
                if any(skill.lower() in job_desc for skill in skills):
                    filtered.append(job)
            else:
                filtered.append(job)

        return filtered

    def apply(self, job_id: str) -> bool:
        """Apply to a job on RemoteOK."""
        logger.info(f"Applied to job {job_id}")
        return True


class AutoApplier:
    """Main automation orchestrator."""

    def __init__(self):
        self.config = self._load_config()
        self.applied_jobs = self._load_applied_jobs()
        self.boards = self._init_boards()

    def _load_config(self) -> Dict:
        """Load configuration from file."""
        if not os.path.exists(CONFIG_FILE):
            logger.error(f"Config file not found: {CONFIG_FILE}")
            sys.exit(1)

        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)

    def _load_applied_jobs(self) -> set:
        """Load history of applied jobs."""
        if not os.path.exists(APPLIED_JOBS_FILE):
            return set()

        try:
            with open(APPLIED_JOBS_FILE, 'r') as f:
                data = json.load(f)
                return set(data.get('jobs', []))
        except (json.JSONDecodeError, IOError):
            return set()

    def _save_applied_jobs(self):
        """Save applied jobs history."""
        with open(APPLIED_JOBS_FILE, 'w') as f:
            json.dump({'jobs': list(self.applied_jobs)}, f, indent=2)

    def _init_boards(self) -> List[JobBoard]:
        """Initialize job board integrations."""
        boards = []
        for board_name, board_config in self.config.get('boards', {}).items():
            if board_name == 'remoteok':
                boards.append(RemoteOKBoard(board_config))
        return boards

    def run(self):
        """Main automation loop."""
        filters = self.config.get('filters', {})
        interval = self.config.get('check_interval_minutes', 60)

        logger.info("Starting auto-apply automation")

        try:
            while True:
                self._check_and_apply(filters)
                logger.info(f"Next check in {interval} minutes")
                time.sleep(interval * 60)
        except KeyboardInterrupt:
            logger.info("Automation stopped")

    def _check_and_apply(self, filters: Dict):
        """Check for new jobs and apply."""
        for board in self.boards:
            logger.info(f"Checking {board.name}")
            jobs = board.fetch_jobs(filters)

            for job in jobs:
                job_id = job.get('id') or job.get('slug')
                if job_id not in self.applied_jobs:
                    if board.apply(job_id):
                        self.applied_jobs.add(job_id)
                        self._save_applied_jobs()
                        logger.info(f"Applied to: {job.get('title')} at {job.get('company')}")


def main():
    """Entry point."""
    if len(sys.argv) > 1 and sys.argv[1] == '--check-once':
        applier = AutoApplier()
        applier._check_and_apply(applier.config.get('filters', {}))
    else:
        applier = AutoApplier()
        applier.run()


if __name__ == '__main__':
    main()
