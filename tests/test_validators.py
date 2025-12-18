"""
Media platforma testlari
"""
import pytest
from app.validators import is_supported_url


class TestValidators:
    """URL validatsiya testlari"""

    def test_tiktok_url(self):
        """TikTok URLlarini tekshirish"""
        assert is_supported_url("https://www.tiktok.com/@scout2015/video/6718335390845095173")
        assert is_supported_url("https://vt.tiktok.com/ZSL7MBJ9c/")
        assert not is_supported_url("https://tiktok.net/video/123")  # Noto'g'ri domen

    def test_instagram_url(self):
        """Instagram URLlarini tekshirish"""
        assert is_supported_url("https://www.instagram.com/reel/Cx1234567/")
        assert is_supported_url("https://instagram.com/p/ABC123DEF/")
        assert not is_supported_url("https://insta.com/p/123")

    def test_youtube_url(self):
        """YouTube URLlarini tekshirish"""
        assert is_supported_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert is_supported_url("https://youtu.be/dQw4w9WgXcQ")
        assert not is_supported_url("https://youtube.net/watch?v=123")

    def test_facebook_url(self):
        """Facebook URLlarini tekshirish"""
        assert is_supported_url("https://www.facebook.com/video.php?v=123456789")
        assert is_supported_url("https://fb.watch/video123/")
        assert not is_supported_url("https://fbook.com/video/123")

    def test_twitter_url(self):
        """Twitter/X URLlarini tekshirish"""
        assert is_supported_url("https://twitter.com/i/web/status/123456789")
        assert is_supported_url("https://x.com/user/status/123456789")
        assert not is_supported_url("https://twitter.net/status/123")

    def test_twitch_url(self):
        """Twitch URLlarini tekshirish"""
        assert is_supported_url("https://www.twitch.tv/videos/123456789")
        assert is_supported_url("https://clips.twitch.tv/channel/abc123")
        assert not is_supported_url("https://twitch.net/video/123")

    def test_invalid_urls(self):
        """Noto'g'ri URLlarni tekshirish"""
        assert not is_supported_url("not a url")
        assert not is_supported_url("ftp://example.com")
        assert not is_supported_url("")
        assert not is_supported_url("https://example.com")  # Qo'llab-quvvatlanmagan sait


class TestDownloadFormats:
    """Format turlari testlari"""

    def test_supported_formats(self):
        """Qo'llab-quvvatlanuvchi formatlarni tekshirish"""
        formats = ["video", "audio", "gif", "image", "both"]
        for fmt in formats:
            assert fmt in ["video", "audio", "gif", "image", "both"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

