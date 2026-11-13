# Независимое ревью, 2026-11-13

Reviewer: отдельный fresh-context агент review_published_instructions,
gpt-6.1-sol/high. Read-only. Охват: бюджеты v3, verify-project-facts и
choose-effective-solution; current canonical, raw evidence и контракты заявок.

Important: rule-budgets.md:14, v3 потерял прежнее условие «For exceedances» перед
approval stop. По буквальному контракту ожидание стало безусловным, включая
W=150/T=1000. Согласованное требование останавливает только W>300 либо T>1000.
Mixed boundary fixtures содержат превышения и не проверяют compliant-only
продолжение. Других Critical/Important/Minor не найдено.

Ревью не оценивало Claude (нет native evidence), следующие заявки/чужие dirty
изменения, human-guide prose (исключена правилами), переносимость реальных
performance/causal claims из синтетических fixtures. Отчёты эти пределы сохраняют.

Результат проверен по сравнению v2/v3 и исходной условной формулировке заявки:
это подтверждённая потеря условия при сжатии, не запрос нового поведения.
Гипотеза проверки: буквальная v3 может требовать лишнее решение перед уже
согласованной локальной стадией даже при бюджете в допустимых границах.
Проверка будет новым compliant-only native fixture; прежние raw/report не правятся.
