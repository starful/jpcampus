import unittest

from fastapi.testclient import TestClient

from app.main import DOMAIN, app
from app.utils import load_guides, load_school_data


class ShareBarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_guide_detail_has_share_bar(self):
        guides = load_guides("en")
        slug = next(g["link"].split("/")[-1].split("?")[0] for g in guides if g.get("link"))
        response = self.client.get(f"/guide/{slug}")
        self.assertEqual(response.status_code, 200)
        html = response.text
        self.assertIn("share-bar", html)
        self.assertIn("share-btn-x", html)
        self.assertIn(f"/card/guide/{slug}", html)
        self.assertIn(f'/social/guide-{slug}.jpg', html)

    def test_school_detail_has_share_bar(self):
        schools, _ = load_school_data("en")
        school_id = next(s["id"] for s in schools if s.get("id"))
        response = self.client.get(f"/school/{school_id}")
        self.assertEqual(response.status_code, 200)
        html = response.text
        self.assertIn("share-bar", html)
        self.assertIn(f"/card/school/{school_id}", html)

    def test_social_card_page(self):
        response = self.client.get("/card/guide/housing")
        self.assertEqual(response.status_code, 200)
        self.assertIn(f'property="og:url" content="{DOMAIN}/card/guide/housing?sc=2"', response.text)

    def test_social_image_served_from_static(self):
        response = self.client.get("/social/guide-housing.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("image/jpeg"))
        self.assertGreater(len(response.content), 1000)
        self.assertEqual(response.headers.get("cache-control"), "public, max-age=604800")

    def test_social_image_head(self):
        response = self.client.head("/social/guide-housing.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("image/jpeg"))
        self.assertEqual(response.content, b"")

    def test_social_image_missing_uses_placeholder_fast(self):
        response = self.client.get("/social/univ_fukuoka-prefectural-university-guide.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("image/jpeg"))
        self.assertGreater(len(response.content), 500)

    def test_resolve_social_jpeg_skips_remote_by_default(self):
        from app.social_share import placeholder_social_jpeg, resolve_social_jpeg

        data = resolve_social_jpeg("https://images.unsplash.com/photo-1541339907198-e08756dedf3f?w=500")
        self.assertEqual(data, placeholder_social_jpeg())

    def test_social_card_head(self):
        response = self.client.head("/card/guide/housing")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertEqual(response.content, b"")


if __name__ == "__main__":
    unittest.main()
