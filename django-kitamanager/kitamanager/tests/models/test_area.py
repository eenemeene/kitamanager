import pytest
from django.db.utils import IntegrityError

from kitamanager.models import Area


@pytest.mark.django_db
def test_area_create():
    """
    Create a single Area and try the same Area again
    """
    Area.objects.create(name="area1", educational=True)

    # 2nd one with different name should work
    Area.objects.create(name="area2", educational=True)

    # 2nd one with same name is not allowed
    with pytest.raises(IntegrityError):
        Area.objects.create(name="area1", educational=False)
