from __future__ import annotations

from unittest.mock import patch

from agent_reach_tech.channels.reddit import RedditChannel


@patch.object(RedditChannel, "http_get_json", return_value={"data": [{"title": "t", "url": "u", "subreddit": "netsec", "score": 1, "num_comments": 0, "created_utc": 1, "selftext": ""}]})
def test_search(mock_get):
    items = RedditChannel().search("cve", limit=1)
    assert len(items) == 1
    assert items[0]["subreddit"] == "netsec"