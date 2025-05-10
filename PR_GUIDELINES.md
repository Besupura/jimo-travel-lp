# Pull Request Guidelines – jimo-travel-lp

## 1. 前提
- **ベースブランチ**: `main`
- **開発ブランチ命名**: `feature/<topic>` / `fix/<topic>` / `hotfix/<topic>`
- **コミット規約**: [Conventional Commits](https://www.conventionalcommits.org/)  
  例) `feat: LP hero section with responsive slideshow`

---

## 2. PR タイトル例
| 目的 | 書式 | 例 |
|------|------|----|
| 新機能 | `feat: <機能概要>` | `feat: add itinerary signup CTA` |
| バグ修正 | `fix: <不具合概要>` | `fix: wrong logo path on production build` |
| ドキュメント | `docs: <対象ファイル>` | `docs: update FAQ links` |
| リファクタ | `refactor: <対象範囲>` | `refactor: extract Map component` |

---

## 3. PR 説明欄テンプレ
```md
### 概要
<!-- 何を / なぜ -->

### 関連 Issue
close #123

### 変更点
- LP ヒーロー画像を WebP 化
- ページロード時の CLS 低減

### 動作確認
- [ ] `npm run dev` で hero が正しく表示される
- [ ] Lighthouse パフォーマンス 90 以上

### スクリーンショット
| Before | After |
|--------|-------|
| ![](before.png) | ![](after.png) |

### 影響範囲
- TopPage のみ（他ページへの副作用なし）

### レビューポイント
1. 画像パスの書き換え漏れがないか
2. WebP 未対応ブラウザ fallback

### 参考資料
- [WebP fallback best practices](https://web.dev/webp/)
