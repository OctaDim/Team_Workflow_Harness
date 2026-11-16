# Transfer Git/PR text as data

Use a structured tool/API parameter without constructing shell code. With CLI,
write text safely as file data; use the body's body-file option or git commit -F.
Create the file without executable substitutions. Pass paths and titles safely too.
JSON serialization inserted into a shell string is not shell escaping.
Preserve intended Markdown, quotes and newlines; protect every shell-sensitive
construct, not only backticks. Verify the actually saved title/body/message.
This resource performs no commit and grants no history rewrite or PR action.
