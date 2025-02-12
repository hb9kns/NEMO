### {{ title }}

> {{ task.problem_description|truncatewords:12 }}

> {{ status_message }}

> ({{ notification_message }})

#### Progress of the task:

> {{ task.progress_description|linebreaks }}

---

See `{{ tool_control_absolute_url|urlize }}` for details!

*automatic message sent by [NEMO/FIRST]( https://nemo.first.ethz.ch )*
