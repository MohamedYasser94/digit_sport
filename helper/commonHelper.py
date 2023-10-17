from core.models.core import SystemSetting

try:
    system_setting = SystemSetting.objects.get_or_create(title='Digithup')

    BACKEND_TEMPLATES=SystemSetting.objects.get(title='Digithup').backend_temp
except Exception as e:
   
    BACKEND_TEMPLATES='good'


try:
    FRONTEND_TEMPLATES=SystemSetting.objects.get(title='Digithup').frontend_temp
except:
    FRONTEND_TEMPLATES='creasoon'

try:
    MAINTENANCE_TEMPLATES=SystemSetting.objects.get(title='Digithup').maintenance_temp
except:
    MAINTENANCE_TEMPLATES='creasoon'



