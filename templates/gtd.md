# GTD Brief for {{ data.date.strftime("%Y/%m/%d") }} (generated on {{ data.timestamp.strftime("%d @ %H:%M:%S") }} UTC)

{% for list in data.lists %}

# {{ list.title }}
{% for ctx in list.ctxs %}
## {{ ctx }}
{% for note in list.by_ctx[ctx] %}
- [ ] {{ note.title }}
{% endfor %}
{% endfor %}

{% if list.title == "Nexts" %}
# Upcomings
{% for note in data.upcoming.list|sort(attribute='due_date') %}
- [ ] {{ note.due_date }} : {{ note.title }}
{% endfor %}
{% endif %}

{% endfor %}


# Projects
{% for prj in data.projects.prjs %}
## {{ prj }}
{% for note in data.projects.by_prj[prj] %}
- [ ] {{ note.title }}
{% endfor %}
{% endfor %}
