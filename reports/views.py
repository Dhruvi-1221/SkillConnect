from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Report
from .forms import ReportForm


@login_required
def submit_report_view(request, target_type, target_id):
    target_type = target_type.upper()
    valid_types = ['USER', 'POST', 'COMMENT', 'SERVICE']
    if target_type not in valid_types:
        messages.error(request, "Invalid report target type.")
        return redirect('home')

    if request.method == 'POST':
        form = ReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            report.target_type = target_type
            report.target_id = target_id
            report.status = 'PENDING'
            report.save()

            messages.success(request, "Report submitted successfully. SkillConnect administrators will investigate and take appropriate action.")
            return redirect('home')
    else:
        form = ReportForm(initial={'target_type': target_type, 'target_id': target_id})

    return render(request, 'reports/submit_report.html', {
        'form': form,
        'target_type': target_type,
        'target_id': target_id,
    })
