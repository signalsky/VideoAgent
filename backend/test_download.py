import unittest
from download import get_youtube_video_id

class TestGetYoutubeVideoId(unittest.TestCase):
    def test_valid_url(self):
        url = 'https://www.youtube.com/watch?v=qYNweeDHiyU'
        result = get_youtube_video_id(url)
        self.assertEqual(result, 'qYNweeDHiyU')

    def test_no_video_id(self):
        url = 'https://www.youtube.com/watch'
        result = get_youtube_video_id(url)
        self.assertEqual(result, None)


if __name__ == '__main__':
    unittest.main()
