"""前端 API 对接测试（验证新前端已对接真实后端路由）"""
import unittest
from pathlib import Path


class TestFrontendIntegration(unittest.TestCase):
    """验证前端文件结构和类型定义。"""

    BASE_DIR = Path(__file__).parent.parent.parent / "shuntian-web" / "src"

    def test_backend_service_exists(self):
        path = self.BASE_DIR / "lib" / "backend.ts"
        self.assertTrue(path.exists(), "backend.ts 不存在")

    def test_types_exist(self):
        path = self.BASE_DIR / "types" / "index.ts"
        self.assertTrue(path.exists(), "types/index.ts 不存在")

    def test_page_files_exist(self):
        for page in ["app/page.tsx", "app/onboarding/page.tsx", "app/me/page.tsx"]:
            path = self.BASE_DIR / page
            self.assertTrue(path.exists(), f"{page} 不存在")

    def test_backend_service_has_required_functions(self):
        content = (self.BASE_DIR / "lib" / "backend.ts").read_text(encoding='utf-8')
        # 新前端对接真实后端路由
        for fn in ['fetchPublicToday', 'validateProfile', 'extractMissingFields']:
            self.assertIn(fn, content, f"缺少函数: {fn}")

    def test_types_have_required_exports(self):
        content = (self.BASE_DIR / "types" / "index.ts").read_text(encoding='utf-8')
        for t in ['PublicTodayCard', 'ProfileStatus', 'StoredProfile', 'ApiError']:
            self.assertIn(t, content, f"缺少类型: {t}")

    def test_onboarding_uses_validate_profile(self):
        content = (self.BASE_DIR / "app" / "onboarding" / "page.tsx").read_text(encoding='utf-8')
        self.assertIn('validateProfile', content)
        self.assertIn('missingFields', content)

    def test_today_uses_fetch_public_today(self):
        content = (self.BASE_DIR / "app" / "page.tsx").read_text(encoding='utf-8')
        self.assertIn('fetchPublicToday', content)
        self.assertIn('DailyGuideResponse', content)

    def test_no_hardcoded_url(self):
        content = (self.BASE_DIR / "lib" / "backend.ts").read_text(encoding='utf-8')
        self.assertNotIn("BASE_URL = 'http://localhost'", content)

    def test_gender_no_default(self):
        content = (self.BASE_DIR / "app" / "onboarding" / "page.tsx").read_text(encoding='utf-8')
        self.assertNotIn("gender || 'male'", content)
        self.assertNotIn("gender ?? 'male'", content)


if __name__ == '__main__':
    unittest.main()
