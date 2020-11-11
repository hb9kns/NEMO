def lock_selected_interlocks(model_admin, request, queryset):
	for interlock in queryset:
		interlock.lock()


def unlock_selected_interlocks(model_admin, request, queryset):
	for interlock in queryset:
		interlock.unlock()


def synchronize_with_tool_usage(model_admin, request, queryset):
	for interlock in queryset:
		# Ignore interlocks with no tool assigned, and ignore interlocks connected to doors
		try:
			if interlock.door:
				continue
		except:
			pass
		if not interlock.tool:
			continue
		if interlock.tool.in_use():
			interlock.unlock()
		else:
			interlock.lock()
