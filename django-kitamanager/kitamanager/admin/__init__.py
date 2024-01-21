from django.contrib import admin
from kitamanager.models import (
    Area,
    Employee,
    EmployeeContract,
    EmployeeQualification,
    EmployeePaymentPlan,
    EmployeePaymentTable,
    EmployeePaymentTableEntry,
    Child,
    ChildContract,
    ChildPaymentPlan,
    ChildPaymentTable,
    ChildPaymentTableEntry,
    BankAccount,
    BankAccountEntry,
    RevenueName,
    RevenueEntry,
)

from .area import AreaAdmin

from .employee import (
    EmployeeAdmin,
    EmployeeContractAdmin,
    EmployeeQualificationAdmin,
    EmployeePaymentPlanAdmin,
    EmployeePaymentTableAdmin,
    EmployeePaymentTableEntryAdmin,
)

from .child import (
    ChildAdmin,
    ChildContractAdmin,
    ChildPaymentPlanAdmin,
    ChildPaymentTableAdmin,
    ChildPaymentTableEntryAdmin,
)

from .bank import (
    BankAccountAdmin,
    BankAccountEntryAdmin,
)

from .revenue import (
    RevenueNameAdmin,
    RevenueEntryAdmin,
)


admin.site.register(Area, AreaAdmin)
admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeContract, EmployeeContractAdmin)
admin.site.register(EmployeeQualification, EmployeeQualificationAdmin)
admin.site.register(EmployeePaymentPlan, EmployeePaymentPlanAdmin)
admin.site.register(EmployeePaymentTable, EmployeePaymentTableAdmin)
admin.site.register(EmployeePaymentTableEntry, EmployeePaymentTableEntryAdmin)
admin.site.register(Child, ChildAdmin)
admin.site.register(ChildContract, ChildContractAdmin)
admin.site.register(ChildPaymentPlan, ChildPaymentPlanAdmin)
admin.site.register(ChildPaymentTable, ChildPaymentTableAdmin)
admin.site.register(ChildPaymentTableEntry, ChildPaymentTableEntryAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
admin.site.register(BankAccountEntry, BankAccountEntryAdmin)
admin.site.register(RevenueName, RevenueNameAdmin)
admin.site.register(RevenueEntry, RevenueEntryAdmin)
