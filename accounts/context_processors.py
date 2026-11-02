def auth_roles_context(request):
    """Provides role flags and verification status to all templates."""
    if not request.user.is_authenticated:
        return {
            'is_student': False,
            'is_customer': False,
            'is_verified_student': False,
            'student_profile': None,
        }
    
    user = request.user
    is_student = getattr(user, 'is_student', False)
    is_customer = getattr(user, 'is_customer', False)
    
    student_profile = None
    is_verified_student = False
    if is_student and hasattr(user, 'student_profile'):
        student_profile = user.student_profile
        is_verified_student = student_profile.verification_status == 'VERIFIED'
        
    return {
        'is_student': is_student,
        'is_customer': is_customer,
        'is_verified_student': is_verified_student,
        'student_profile': student_profile,
    }
