from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from core.models import NGO, Need, Donation, UtilizationReport
from decimal import Decimal
import uuid

class Command(BaseCommand):
    help = 'Seeds the database with sample NGOs, needs, donations and reports'

    def handle(self, *args, **kwargs):
        if NGO.objects.exists():
            self.stdout.write('Database already seeded. Skipping.')
            return

        # Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@daan.org', 'admin123')
            self.stdout.write('Created superuser: admin / admin123')

        # Donors
        users = []
        for uname, email in [('priya_r','priya@ex.com'),('rahul_m','rahul@ex.com'),('ananya_s','ananya@ex.com')]:
            u, _ = User.objects.get_or_create(username=uname, defaults={'email': email})
            u.set_password('pass1234')
            u.save()
            users.append(u)

        # NGOs
        ngos = []
        for d in [
            ('Shiksha Hope Foundation', 'Providing quality education to underprivileged children in rural Karnataka through community schools and digital learning centers.', 'education', 'Bengaluru, Karnataka', 'NGO-EDU-001', 'shiksha@hope.org', '+91-80-4567', 'SHF', 2018),
            ('Aarogya Health Trust', 'Delivering affordable primary healthcare to tribal communities through mobile medical units and telemedicine technology.', 'health', 'Udupi, Karnataka', 'NGO-HLT-002', 'aarogya@trust.org', '+91-820-234', 'AHT', 2019),
            ('Prakriti Environmental Society', 'Restoring degraded forests and wetlands while empowering local communities as environmental stewards of their land.', 'environment', 'Coorg, Karnataka', 'NGO-ENV-003', 'prakriti@soc.org', '+91-8272-234', 'PES', 2020),
            ('Anna Daata Food Network', 'Fighting food insecurity through community kitchens, food banks, and sustainable agriculture training for small farmers.', 'food', 'Mysuru, Karnataka', 'NGO-FD-004', 'anna@daata.org', '+91-821-345', 'ADF', 2017),
            ('Shakti Women Collective', 'Empowering women through skill development, microfinance, and legal aid programs across urban slums and rural areas.', 'women', 'Mangaluru, Karnataka', 'NGO-WMN-005', 'shakti@col.org', '+91-824-456', 'SWC', 2021),
        ]:
            n = NGO.objects.create(
                name=d[0], description=d[1], category=d[2], location=d[3],
                registration_number=d[4], contact_email=d[5], contact_phone=d[6],
                logo_initial=d[7], founded_year=d[8], status='approved', verified=True
            )
            ngos.append(n)

        # Needs
        for ngo, title, req, raised, prio in [
            (ngos[0], 'Digital Tablets for Rural Schools', 300000, 219000, 'urgent'),
            (ngos[0], 'Teacher Training Workshop', 80000, 52000, 'high'),
            (ngos[1], 'Mobile Medical Van', 1500000, 875000, 'urgent'),
            (ngos[1], 'Medicines for Tribal Clinics', 120000, 78000, 'high'),
            (ngos[2], 'Sapling Plantation Drive', 50000, 31000, 'medium'),
            (ngos[3], 'Community Kitchen Equipment', 250000, 190000, 'high'),
            (ngos[4], 'Sewing Machines for Women', 90000, 45000, 'medium'),
        ]:
            Need.objects.create(
                ngo=ngo, title=title, description=title,
                amount_required=Decimal(req), amount_raised=Decimal(raised),
                priority=prio, is_active=True
            )

        # Donations
        amts = [5000, 2500, 10000, 1000, 7500, 3000, 500, 15000, 2000, 4000]
        for i, ngo in enumerate(ngos):
            for j, user in enumerate(users):
                Donation.objects.create(
                    donor=user, ngo=ngo, donation_type='monetary',
                    amount=Decimal(amts[(i * 3 + j) % len(amts)]),
                    message='Keep up the amazing work!',
                    status='completed', anonymous=(j == 2),
                    transaction_id=str(uuid.uuid4())[:12].upper()
                )

        # Utilization Reports
        for ngo, title, desc, bcount, used in [
            (ngos[0], 'Tablets Deployed in 3 Schools', 'We successfully deployed 60 tablets across 3 village schools with 40% improvement in digital literacy.', 120, 90000),
            (ngos[1], '500 Patients Treated in October', 'Our mobile van visited 8 villages providing free consultations and medicines to 500 tribal residents.', 500, 75000),
            (ngos[2], '3000 Saplings Planted', 'Community volunteers planted 3000 native saplings with 82% survival rate after 6 months.', 0, 18000),
        ]:
            UtilizationReport.objects.create(
                ngo=ngo, title=title, description=desc,
                impact_description=desc, beneficiaries_count=bcount,
                amount_used=Decimal(used)
            )

        self.stdout.write(self.style.SUCCESS(
            f'Seeded: {NGO.objects.count()} NGOs, {Need.objects.count()} needs, '
            f'{Donation.objects.count()} donations, {UtilizationReport.objects.count()} reports'
        ))
