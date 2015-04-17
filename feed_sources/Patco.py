"""Fetch unofficial PATCO feed."""

from datetime import datetime
import logging
import requests

from FeedSource import FeedSource, TIMECHECK_FMT

URL = 'https://api.github.com/repos/flibbertigibbet/patco-gtfs/releases/latest'
FILE_NAME = 'patco.zip'

LAST_UPDATED_FMT = '%Y-%m-%dT%H:%M:%SZ'

LOG = logging.getLogger(__name__)


class Patco(FeedSource):
    """Fetch unofficial PATCO feed."""
    def __init__(self):
        super(Patco, self).__init__()
        self.urls = {'patco.zip': URL}

    def fetch(self):
        """Check GitHub latest release page to see if there is a newer download available."""
        request = requests.get(URL)
        if request.ok:
            response = request.json()
            download_url = response['assets'][0]['browser_download_url']
            last_updated_str = response['assets'][0]['updated_at']
            last_updated = datetime.strptime(last_updated_str, LAST_UPDATED_FMT)
            got_last_str = self.timecheck.get(FILE_NAME)
            if got_last_str:
                got_last = datetime.strptime(got_last_str, TIMECHECK_FMT)
                LOG.debug('PATCO GTFS last fetched: %s, last updated: %s', got_last, last_updated)
                if got_last >= last_updated:
                    LOG.info('No new download available for PATCO.')
                    return
            else:
                LOG.info('No previous PATCO download found. Last update posted: %s', last_updated)

            if self.fetchone(FILE_NAME, download_url):
                self.timecheck[FILE_NAME] = last_updated.strftime(TIMECHECK_FMT)
                self.write_timecheck()
        else:
            LOG.error('Could not check GitHub relases page for PATCO.')
