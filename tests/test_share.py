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
        self.assertIn(f'property="og:url" content="{DOMAIN}/card/guide/housing"', response.text)

    def test_social_image_endpoint(self):
        response = self.client.get("/social/guide-housing.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("image/jpeg"))
        self.assertGreater(len(response.content), 1000)

    def test_social_image_head(self):
        response = self.client.head("/social/guide-housing.jpg")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.headers["content-type"].startswith("image/jpeg"))
        self.assertEqual(response.content, b"")

    def test_social_card_head(self):
        response = self.client.head("/card/guide/housing")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.headers["content-type"])
        self.assertEqual(response.content, b"")


if __name__ == "__main__":
    unittest.main()
