import unittest

from fastapi.testclient import TestClient

from app.main import app, DOMAIN
from app.utils import load_school_data, load_guides


class RouteSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_core_routes_return_200(self):
        for path in ["/", "/schools", "/universities", "/guide", "/about", "/policy", "/contact", "/compare"]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)

    def test_core_routes_have_canonical(self):
        target = self.client.get("/schools")
        self.assertIn(f'<link rel="canonical" href="{DOMAIN}/schools">', target.text)

    def test_sitemap_contains_lastmod_and_hreflang(self):
        response = self.client.get("/sitemap.xml")
        self.assertEqual(response.status_code, 200)
        self.assertIn("<lastmod>", response.text)
        self.assertIn('hreflang="en"', response.text)
        self.assertIn('hreflang="ko"', response.text)

    def test_legacy_redirect_map(self):
        response = self.client.get("/privacy", follow_redirects=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers.get("location"), "/policy")

    def test_add_compare_query_redirects_to_school(self):
        response = self.client.get(
            "/?lang=en&add_compare=univ_shiga-university-guide",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers.get("location"), "/school/univ_shiga-university-guide")

    def test_add_compare_preserves_korean_lang(self):
        response = self.client.get(
            "/?lang=kr&add_compare=school_asuka-gakuin",
            follow_redirects=False,
        )
        self.assertEqual(response.status_code, 301)
        self.assertEqual(
            response.headers.get("location"),
            "/school/school_asuka-gakuin?lang=kr",
        )

    def test_explicit_lang_en_redirects_to_bare_path(self):
        response = self.client.get("/universities?lang=en", follow_redirects=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers.get("location"), "/universities")

    def test_legacy_school_code_redirects_to_schools_hub(self):
        response = self.client.get("/school/L002", follow_redirects=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers.get("location"), "/schools")

    def test_legacy_univ_code_redirects_to_universities_hub(self):
        response = self.client.get("/school/U_TOKYO", follow_redirects=False)
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.headers.get("location"), "/universities")

    def test_robots_disallows_card_and_add_compare(self):
        response = self.client.get("/robots.txt")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Disallow: /card/", response.text)
        self.assertIn("Disallow: /*?add_compare=", response.text)
        self.assertIn(f"Sitemap: {DOMAIN}/sitemap.xml", response.text)

    def test_reactions_api_returns_counts(self):
        response = self.client.get("/api/reactions/smoke-test-slug")
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("likes", payload)
        self.assertIn("dislikes", payload)

    def test_sample_detail_pages_render(self):
        schools, _ = load_school_data("en")
        school_id = next((s.get("id") for s in schools if s.get("id")), None)
        self.assertIsNotNone(school_id)
        school_response = self.client.get(f"/school/{school_id}")
        self.assertEqual(school_response.status_code, 200)

        guides = load_guides("en")
        guide_slug = next((g["link"].split("/")[-1].split("?")[0] for g in guides if g.get("link")), None)
        self.assertIsNotNone(guide_slug)
        guide_response = self.client.get(f"/guide/{guide_slug}")
        self.assertEqual(guide_response.status_code, 200)
        self.assertIn("reaction-panel", guide_response.text)
        self.assertIn("share-bar", guide_response.text)
        self.assertIn("count-like", school_response.text)

    def test_favicon_and_manifest_routes_exist(self):
        for path in [
            "/favicon.ico",
            "/favicon-32x32.png",
            "/favicon-48x48.png",
            "/apple-touch-icon.png",
            "/site.webmanifest",
        ]:
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
