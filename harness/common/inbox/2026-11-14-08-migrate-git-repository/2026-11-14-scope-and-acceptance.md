# Область и сценарии comm-migrate-git-repository

Дата создания: 2026-11-14.

Это план будущего исполнения, не журнал прошедших проверок.

- **13. Миграция репозитория:** Согласовать исходный/целевой repo, цель transfer/rename/copy/cross-host, сохраняемые свойства и метод. Сравнить native transfer и import/mirror. Инвентарь refs/history/LFS/metadata/rights/protections/apps/hooks/runners/automation/docs по применимости. Проверить URL-формы, корректные старые имена и историю. Host-specific редиректы/возможности проверять по текущим данным. Нет автоматического удаления/перезаписи/расширения доступов. Проверить существенные свойства/интеграции; production и secrets отдельно.

## Сценарии

- Native transfer против copy/import/mirror и сохраняемых свойств.
- Неоднозначная идентичность, ограничения получателя/protections/permissions.
- SSH/API/raw/PR ссылки и правильное старое имя runner-service.
- Redirect reuse, LFS/metadata и интеграция не переносятся по одному git diff.
- Mirror не разрешает запрещённое удаление/перезапись или production-проверку.
