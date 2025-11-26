# Data migration to seed UK media outlets
from django.db import migrations


def seed_media_outlets(apps, schema_editor):
    """Seed the database with UK media outlets for complaints"""
    MediaOutlet = apps.get_model('media_complaints', 'MediaOutlet')

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
        {
            'name': 'BBC Newsnight',
            'media_type': 'tv',
            'contact_email': 'newsnight@bbc.co.uk',
            'complaints_dept_email': 'complaints@bbc.co.uk',
            'website': 'https://www.bbc.co.uk/programmes/b006mk25',
            'regulator': 'Ofcom',
            'description': 'BBC Newsnight current affairs programme'
        },
        {
            'name': 'BBC Today Programme',
            'media_type': 'radio',
            'contact_email': 'today@bbc.co.uk',
            'complaints_dept_email': 'complaints@bbc.co.uk',
            'website': 'https://www.bbc.co.uk/programmes/b006qj9z',
            'regulator': 'Ofcom',
            'description': 'BBC Radio 4 Today Programme'
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
        {
            'name': 'Peston',
            'media_type': 'tv',
            'contact_email': 'viewerservices@itv.com',
            'complaints_dept_email': 'viewerservices@itv.com',
            'website': 'https://www.itv.com/peston',
            'regulator': 'Ofcom',
            'description': 'ITV Peston political interview show'
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

        # GB News
        {
            'name': 'GB News',
            'media_type': 'tv',
            'contact_email': 'contact@gbnews.uk',
            'complaints_dept_email': 'complaints@gbnews.uk',
            'website': 'https://www.gbnews.com',
            'regulator': 'Ofcom',
            'description': 'GB News television channel'
        },

        # Talk TV
        {
            'name': 'TalkTV',
            'media_type': 'tv',
            'contact_email': 'talktv@news.co.uk',
            'complaints_dept_email': 'talktv@news.co.uk',
            'website': 'https://www.talktv.co.uk',
            'regulator': 'Ofcom',
            'description': 'TalkTV news and opinion channel'
        },

        # Print Media - Broadsheets
        {
            'name': 'The Guardian',
            'media_type': 'print',
            'contact_email': 'reader@theguardian.com',
            'complaints_dept_email': 'userhelp@theguardian.com',
            'website': 'https://www.theguardian.com',
            'regulator': 'IPSO',
            'description': 'The Guardian newspaper and online. Note: The Guardian is NOT a member of IPSO but has its own readers\' editor system.'
        },
        {
            'name': 'The Observer',
            'media_type': 'print',
            'contact_email': 'reader@observer.co.uk',
            'complaints_dept_email': 'userhelp@theguardian.com',
            'website': 'https://www.theguardian.com/observer',
            'regulator': 'IPSO',
            'description': 'The Observer Sunday newspaper (sister paper to The Guardian)'
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
            'name': 'The Sunday Times',
            'media_type': 'print',
            'contact_email': 'editor@sunday-times.co.uk',
            'complaints_dept_email': 'complaints@sunday-times.co.uk',
            'website': 'https://www.thetimes.co.uk/sunday-times',
            'regulator': 'IPSO',
            'description': 'The Sunday Times newspaper'
        },
        {
            'name': 'The Telegraph',
            'media_type': 'print',
            'contact_email': 'dt.letters@telegraph.co.uk',
            'complaints_dept_email': 'complaints@telegraph.co.uk',
            'website': 'https://www.telegraph.co.uk',
            'regulator': 'IPSO',
            'description': 'The Daily Telegraph newspaper'
        },
        {
            'name': 'The Sunday Telegraph',
            'media_type': 'print',
            'contact_email': 'st.letters@telegraph.co.uk',
            'complaints_dept_email': 'complaints@telegraph.co.uk',
            'website': 'https://www.telegraph.co.uk',
            'regulator': 'IPSO',
            'description': 'The Sunday Telegraph newspaper'
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
            'name': 'The i newspaper',
            'media_type': 'print',
            'contact_email': 'letters@inews.co.uk',
            'complaints_dept_email': 'complaints@inews.co.uk',
            'website': 'https://inews.co.uk',
            'regulator': 'IPSO',
            'description': 'The i newspaper and inews.co.uk'
        },

        # Print Media - Tabloids
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
            'name': 'The Mail on Sunday',
            'media_type': 'print',
            'contact_email': 'news@mailonsunday.co.uk',
            'complaints_dept_email': 'editorial.complaints@dailymail.co.uk',
            'website': 'https://www.dailymail.co.uk',
            'regulator': 'IPSO',
            'description': 'The Mail on Sunday newspaper'
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
            'name': 'The Sun on Sunday',
            'media_type': 'print',
            'contact_email': 'exclusive@the-sun.co.uk',
            'complaints_dept_email': 'complaints@the-sun.co.uk',
            'website': 'https://www.thesun.co.uk',
            'regulator': 'IPSO',
            'description': 'The Sun on Sunday newspaper'
        },
        {
            'name': 'Daily Express',
            'media_type': 'print',
            'contact_email': 'letters@express.co.uk',
            'complaints_dept_email': 'complaints@express.co.uk',
            'website': 'https://www.express.co.uk',
            'regulator': 'IPSO',
            'description': 'Daily Express newspaper'
        },
        {
            'name': 'Sunday Express',
            'media_type': 'print',
            'contact_email': 'letters@express.co.uk',
            'complaints_dept_email': 'complaints@express.co.uk',
            'website': 'https://www.express.co.uk',
            'regulator': 'IPSO',
            'description': 'Sunday Express newspaper'
        },
        {
            'name': 'Daily Mirror',
            'media_type': 'print',
            'contact_email': 'mirrornews@mirror.co.uk',
            'complaints_dept_email': 'complaints@mirror.co.uk',
            'website': 'https://www.mirror.co.uk',
            'regulator': 'IPSO',
            'description': 'Daily Mirror newspaper'
        },
        {
            'name': 'Sunday Mirror',
            'media_type': 'print',
            'contact_email': 'mirrornews@mirror.co.uk',
            'complaints_dept_email': 'complaints@mirror.co.uk',
            'website': 'https://www.mirror.co.uk',
            'regulator': 'IPSO',
            'description': 'Sunday Mirror newspaper'
        },
        {
            'name': 'Daily Star',
            'media_type': 'print',
            'contact_email': 'news@dailystar.co.uk',
            'complaints_dept_email': 'complaints@reachplc.com',
            'website': 'https://www.dailystar.co.uk',
            'regulator': 'IPSO',
            'description': 'Daily Star newspaper'
        },
        {
            'name': 'Metro',
            'media_type': 'print',
            'contact_email': 'newsdesk@metro.co.uk',
            'complaints_dept_email': 'complaints@metro.co.uk',
            'website': 'https://metro.co.uk',
            'regulator': 'IPSO',
            'description': 'Metro free newspaper'
        },
        {
            'name': 'Evening Standard',
            'media_type': 'print',
            'contact_email': 'news@standard.co.uk',
            'complaints_dept_email': 'complaints@standard.co.uk',
            'website': 'https://www.standard.co.uk',
            'regulator': 'IPSO',
            'description': 'London Evening Standard newspaper'
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
        {
            'name': 'TalkSport',
            'media_type': 'radio',
            'contact_email': 'studio@talksport.com',
            'complaints_dept_email': 'complaints@talksport.com',
            'website': 'https://talksport.com',
            'regulator': 'Ofcom',
            'description': 'TalkSport radio station'
        },
        {
            'name': 'Talk Radio',
            'media_type': 'radio',
            'contact_email': 'studio@talkradio.co.uk',
            'complaints_dept_email': 'talktv@news.co.uk',
            'website': 'https://www.talkradio.co.uk',
            'regulator': 'Ofcom',
            'description': 'Talk Radio'
        },

        # Online Media
        {
            'name': 'The Independent',
            'media_type': 'online',
            'contact_email': 'newsdesk@independent.co.uk',
            'complaints_dept_email': 'complaints@independent.co.uk',
            'website': 'https://www.independent.co.uk',
            'regulator': 'IPSO',
            'description': 'The Independent online'
        },
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
        {
            'name': 'The Spectator',
            'media_type': 'online',
            'contact_email': 'editor@spectator.co.uk',
            'complaints_dept_email': 'complaints@spectator.co.uk',
            'website': 'https://www.spectator.co.uk',
            'regulator': 'IPSO',
            'description': 'The Spectator magazine and online'
        },
        {
            'name': 'The New Statesman',
            'media_type': 'online',
            'contact_email': 'editor@newstatesman.com',
            'complaints_dept_email': 'editor@newstatesman.com',
            'website': 'https://www.newstatesman.com',
            'regulator': '',
            'description': 'The New Statesman magazine and online'
        },
        {
            'name': 'The Economist',
            'media_type': 'online',
            'contact_email': 'letters@economist.com',
            'complaints_dept_email': 'readerseditor@economist.com',
            'website': 'https://www.economist.com',
            'regulator': '',
            'description': 'The Economist magazine'
        },

        # News Agencies
        {
            'name': 'Reuters UK',
            'media_type': 'online',
            'contact_email': 'london.newsroom@reuters.com',
            'complaints_dept_email': 'london.newsroom@reuters.com',
            'website': 'https://uk.reuters.com',
            'regulator': '',
            'description': 'Reuters UK news agency'
        },
        {
            'name': 'PA Media (Press Association)',
            'media_type': 'online',
            'contact_email': 'news@pa.media',
            'complaints_dept_email': 'news@pa.media',
            'website': 'https://www.pamedia.com',
            'regulator': '',
            'description': 'PA Media (Press Association) news agency'
        },

        # Regional/Scottish
        {
            'name': 'The Scotsman',
            'media_type': 'print',
            'contact_email': 'news@scotsman.com',
            'complaints_dept_email': 'complaints@scotsman.com',
            'website': 'https://www.scotsman.com',
            'regulator': 'IPSO',
            'description': 'The Scotsman newspaper'
        },
        {
            'name': 'The Herald (Scotland)',
            'media_type': 'print',
            'contact_email': 'news@theherald.co.uk',
            'complaints_dept_email': 'complaints@theherald.co.uk',
            'website': 'https://www.heraldscotland.com',
            'regulator': 'IPSO',
            'description': 'The Herald (Glasgow) newspaper'
        },
        {
            'name': 'Daily Record',
            'media_type': 'print',
            'contact_email': 'reporters@dailyrecord.co.uk',
            'complaints_dept_email': 'complaints@reachplc.com',
            'website': 'https://www.dailyrecord.co.uk',
            'regulator': 'IPSO',
            'description': 'Daily Record (Scotland) newspaper'
        },
        {
            'name': 'Wales Online',
            'media_type': 'online',
            'contact_email': 'newsdesk@walesonline.co.uk',
            'complaints_dept_email': 'complaints@reachplc.com',
            'website': 'https://www.walesonline.co.uk',
            'regulator': 'IPSO',
            'description': 'Wales Online news website'
        },
        {
            'name': 'Belfast Telegraph',
            'media_type': 'print',
            'contact_email': 'newsroom@belfasttelegraph.co.uk',
            'complaints_dept_email': 'feedback@belfasttelegraph.co.uk',
            'website': 'https://www.belfasttelegraph.co.uk',
            'regulator': 'IPSO',
            'description': 'Belfast Telegraph newspaper'
        },
    ]

    for outlet_data in outlets_data:
        MediaOutlet.objects.update_or_create(
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


def reverse_seed(apps, schema_editor):
    """Remove seeded outlets (optional for rollback)"""
    # Don't delete outlets on reverse migration as users may have complaints
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('media_complaints', '0002_outletsuggestion'),
    ]

    operations = [
        migrations.RunPython(seed_media_outlets, reverse_seed),
    ]
