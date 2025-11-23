"""Management command to seed UK media outlets"""
from django.core.management.base import BaseCommand
from apps.media_complaints.models import MediaOutlet


class Command(BaseCommand):
    help = 'Seed the database with UK media outlets'

    def handle(self, *args, **kwargs):
        """Seed UK media outlets"""
        self.stdout.write('Seeding media outlets...')

        outlets_data = [
            # BBC
            {
                'name': 'BBC News',
                'media_type': 'tv',
                'contact_email': 'complaints@bbc.co.uk',
                'complaints_dept_email': 'complaints@bbc.co.uk',
                'website': 'https://www.bbc.co.uk/news',
                'regulator': 'Ofcom',
                'description': 'BBC News television broadcasts'
            },
            {
                'name': 'BBC Radio 4',
                'media_type': 'radio',
                'contact_email': 'radio4.complaints@bbc.co.uk',
                'complaints_dept_email': 'complaints@bbc.co.uk',
                'website': 'https://www.bbc.co.uk/radio4',
                'regulator': 'Ofcom',
                'description': 'BBC Radio 4'
            },
            {
                'name': 'BBC Question Time',
                'media_type': 'tv',
                'contact_email': 'bbcquestiontime@bbc.co.uk',
                'complaints_dept_email': 'complaints@bbc.co.uk',
                'website': 'https://www.bbc.co.uk/programmes/b006t1q9',
                'regulator': 'Ofcom',
                'description': 'BBC Question Time political discussion programme'
            },
            {
                'name': 'BBC Politics Live',
                'media_type': 'tv',
                'contact_email': 'bbcnews@bbc.co.uk',
                'complaints_dept_email': 'complaints@bbc.co.uk',
                'website': 'https://www.bbc.co.uk',
                'regulator': 'Ofcom',
                'description': 'BBC Politics Live daily politics show'
            },

            # ITV
            {
                'name': 'ITV News',
                'media_type': 'tv',
                'contact_email': 'duty.office@itv.com',
                'complaints_dept_email': 'viewerservices@itv.com',
                'website': 'https://www.itv.com/news',
                'regulator': 'Ofcom',
                'description': 'ITV News broadcasts'
            },
            {
                'name': 'Good Morning Britain',
                'media_type': 'tv',
                'contact_email': 'gmb@itv.com',
                'complaints_dept_email': 'viewerservices@itv.com',
                'website': 'https://www.itv.com/gmb',
                'regulator': 'Ofcom',
                'description': 'ITV Good Morning Britain breakfast show'
            },

            # Sky
            {
                'name': 'Sky News',
                'media_type': 'tv',
                'contact_email': 'news@sky.uk',
                'complaints_dept_email': 'info@sky.uk',
                'website': 'https://news.sky.com',
                'regulator': 'Ofcom',
                'description': 'Sky News 24-hour news channel'
            },

            # Channel 4
            {
                'name': 'Channel 4 News',
                'media_type': 'tv',
                'contact_email': 'c4news@channel4.co.uk',
                'complaints_dept_email': 'viewerequiries@channel4.co.uk',
                'website': 'https://www.channel4.com/news',
                'regulator': 'Ofcom',
                'description': 'Channel 4 News'
            },

            # Print Media
            {
                'name': 'The Guardian',
                'media_type': 'print',
                'contact_email': 'reader@theguardian.com',
                'complaints_dept_email': 'userhelp@theguardian.com',
                'website': 'https://www.theguardian.com',
                'regulator': 'IPSO',
                'description': 'The Guardian newspaper and online'
            },
            {
                'name': 'The Times',
                'media_type': 'print',
                'contact_email': 'editor@thetimes.co.uk',
                'complaints_dept_email': 'complaints@thetimes.co.uk',
                'website': 'https://www.thetimes.co.uk',
                'regulator': 'IPSO',
                'description': 'The Times newspaper'
            },
            {
                'name': 'The Telegraph',
                'media_type': 'print',
                'contact_email': 'dt.letters@telegraph.co.uk',
                'complaints_dept_email': 'complaints@telegraph.co.uk',
                'website': 'https://www.telegraph.co.uk',
                'regulator': 'IPSO',
                'description': 'The Telegraph newspaper'
            },
            {
                'name': 'Daily Mail',
                'media_type': 'print',
                'contact_email': 'news@dailymail.co.uk',
                'complaints_dept_email': 'editorial.complaints@dailymail.co.uk',
                'website': 'https://www.dailymail.co.uk',
                'regulator': 'IPSO',
                'description': 'Daily Mail newspaper and MailOnline'
            },
            {
                'name': 'The Sun',
                'media_type': 'print',
                'contact_email': 'exclusive@the-sun.co.uk',
                'complaints_dept_email': 'complaints@the-sun.co.uk',
                'website': 'https://www.thesun.co.uk',
                'regulator': 'IPSO',
                'description': 'The Sun newspaper'
            },
            {
                'name': 'Financial Times',
                'media_type': 'print',
                'contact_email': 'letters.editor@ft.com',
                'complaints_dept_email': 'reader.complaints@ft.com',
                'website': 'https://www.ft.com',
                'regulator': 'IPSO',
                'description': 'Financial Times'
            },
            {
                'name': 'The Independent',
                'media_type': 'online',
                'contact_email': 'newsdesk@independent.co.uk',
                'complaints_dept_email': 'complaints@independent.co.uk',
                'website': 'https://www.independent.co.uk',
                'regulator': 'IPSO',
                'description': 'The Independent online'
            },

            # Radio
            {
                'name': 'LBC Radio',
                'media_type': 'radio',
                'contact_email': 'studio@lbc.co.uk',
                'complaints_dept_email': 'complaints@global.com',
                'website': 'https://www.lbc.co.uk',
                'regulator': 'Ofcom',
                'description': 'LBC talk radio'
            },
            {
                'name': 'Times Radio',
                'media_type': 'radio',
                'contact_email': 'hello@timesradio.com',
                'complaints_dept_email': 'hello@timesradio.com',
                'website': 'https://www.thetimes.co.uk/radio',
                'regulator': 'Ofcom',
                'description': 'Times Radio'
            },

            # Online-first
            {
                'name': 'HuffPost UK',
                'media_type': 'online',
                'contact_email': 'ukscoop@huffpost.com',
                'complaints_dept_email': 'ukscoop@huffpost.com',
                'website': 'https://www.huffingtonpost.co.uk',
                'regulator': 'IPSO',
                'description': 'HuffPost UK online news'
            },
            {
                'name': 'PoliticsHome',
                'media_type': 'online',
                'contact_email': 'editor@politicshome.com',
                'complaints_dept_email': 'editor@politicshome.com',
                'website': 'https://www.politicshome.com',
                'regulator': '',
                'description': 'PoliticsHome political news website'
            },
        ]

        created_count = 0
        updated_count = 0

        for outlet_data in outlets_data:
            outlet, created = MediaOutlet.objects.update_or_create(
                name=outlet_data['name'],
                defaults={
                    'media_type': outlet_data['media_type'],
                    'contact_email': outlet_data['contact_email'],
                    'complaints_dept_email': outlet_data['complaints_dept_email'],
                    'website': outlet_data['website'],
                    'regulator': outlet_data['regulator'],
                    'description': outlet_data['description'],
                    'is_active': True
                }
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {outlet.name}'))
            else:
                updated_count += 1
                self.stdout.write(f'  Updated: {outlet.name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nSeeding complete! Created: {created_count}, Updated: {updated_count}'
        ))
