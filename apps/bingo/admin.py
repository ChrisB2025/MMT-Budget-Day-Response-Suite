"""Admin configuration for bingo app"""
from django.contrib import admin
from django.contrib import messages
from .models import BingoPhrase, BingoCard, BingoSquare


@admin.register(BingoPhrase)
class BingoPhraseAdmin(admin.ModelAdmin):
    """Bingo phrase admin"""
    list_display = ['phrase_text', 'difficulty_level', 'category', 'created_at']
    list_filter = ['difficulty_level', 'category']
    search_fields = ['phrase_text', 'description']
    ordering = ['difficulty_level', 'phrase_text']
    actions = ['load_all_budget_phrases']

    def load_all_budget_phrases(self, request, queryset):
        """Load all Budget Day Bingo phrases into the database"""
        from .management.commands.load_budget_phrases import Command

        # Get the phrase data from the management command
        cmd = Command()

        # Clear existing phrases
        deleted_count = BingoPhrase.objects.all().delete()[0]

        # The phrases list from the command
        phrases = [
            # CLASSIC DIFFICULTY (40 phrases)
            {
                'phrase_text': "We've maxed out the national credit card",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "The UK government issues its own currency and cannot 'max out' like a household. It's the monopoly issuer of pounds."
            },
            {
                'phrase_text': "The country is running out of money",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "A currency-issuing government cannot run out of the currency it creates. Only real resources can be exhausted."
            },
            {
                'phrase_text': "We're leaving a mountain of debt for our children",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "Future generations inherit both the debt and the assets it created, plus the productive capacity those assets enabled."
            },
            {
                'phrase_text': "The government has to balance its books like a household",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "Households are currency users, governments are currency issuers. The operations are fundamentally different."
            },
            {
                'phrase_text': "Where's the magic money tree?",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Governments with sovereign currencies create money through keystrokes. The constraint is inflation, not money availability."
            },
            {
                'phrase_text': "We're living beyond our means",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "A nation's 'means' are its real productive capacity, not an arbitrary financial constraint on a currency issuer."
            },
            {
                'phrase_text': "Taxpayers' money is being wasted",
                'category': 'Taxation',
                'difficulty_level': 'classic',
                'description': "Taxes don't fund spending for currency issuers. They create demand for the currency and manage inflation."
            },
            {
                'phrase_text': "We can't afford this spending",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Affordability for currency issuers is about real resources (labour, materials), not pounds."
            },
            {
                'phrase_text': "The government borrowing is out of control",
                'category': 'Borrowing',
                'difficulty_level': 'classic',
                'description': "Government 'borrowing' is just offering interest-bearing savings accounts. It's a monetary operation, not financing constraint."
            },
            {
                'phrase_text': "Future generations will have to pay back this debt",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "The government never needs to 'pay back' debt in aggregate. Bonds mature and are typically rolled over indefinitely."
            },
            {
                'phrase_text': "We need to tighten our belts",
                'category': 'Austerity',
                'difficulty_level': 'classic',
                'description': "Government spending cuts reduce private sector income, often worsening the deficit through reduced tax revenue."
            },
            {
                'phrase_text': "The nation's finances are in ruins",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "Financial capacity and real economic capacity are different. Currency issuers face real resource constraints, not financial ones."
            },
            {
                'phrase_text': "We're mortgaging our children's future",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "Government investment today builds the infrastructure and capabilities that future generations inherit and benefit from."
            },
            {
                'phrase_text': "Taxpayers will be on the hook for this",
                'category': 'Taxation',
                'difficulty_level': 'classic',
                'description': "Government spending creates the income from which taxes are paid. Spending logically and operationally precedes taxation."
            },
            {
                'phrase_text': "The government has run up massive debts",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "Government debt is just the record of pounds not yet taxed back. It represents private sector net savings."
            },
            {
                'phrase_text': "We need to get the deficit down",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "The deficit reflects the private sector's surplus. Reducing the deficit removes income from households and businesses."
            },
            {
                'phrase_text': "This is unaffordable for the British taxpayer",
                'category': 'Taxation',
                'difficulty_level': 'classic',
                'description': "Taxpayers don't fund sovereign government spending. Taxes serve to control inflation and redistribute resources."
            },
            {
                'phrase_text': "The black hole in the public finances",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "There is no hole, black or otherwise. Government deficits add financial assets to the private sector."
            },
            {
                'phrase_text': "We're saddling future generations with debt",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "Government bonds are assets owned by the private sector, including pension funds that benefit future retirees."
            },
            {
                'phrase_text': "The government is spending money it doesn't have",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Currency-issuing governments create money when they spend. They cannot spend money they don't have."
            },
            {
                'phrase_text': "We need to live within our means as a country",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "Real means are productive capacity and resources, not arbitrary financial limits on a currency-issuing government."
            },
            {
                'phrase_text': "This will bankrupt the nation",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "A government that issues its own free-floating currency cannot go bankrupt in that currency."
            },
            {
                'phrase_text': "We're robbing our grandchildren",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "Investments in infrastructure, education, and climate create the productive capacity grandchildren will inherit."
            },
            {
                'phrase_text': "Hard-working families will pay for this",
                'category': 'Taxation',
                'difficulty_level': 'classic',
                'description': "Government spending creates the income that families earn. Spending comes first, taxation comes after."
            },
            {
                'phrase_text': "The government must balance the budget",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "A government surplus means the private sector runs a deficit, removing savings from households and businesses."
            },
            {
                'phrase_text': "We can't just print money",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Modern government spending is electronic crediting of bank accounts, not printing. The constraint is inflation, not money creation."
            },
            {
                'phrase_text': "The national debt is spiralling out of control",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "For a currency issuer, debt sustainability is about inflation risk, not ability to make payments in its own currency."
            },
            {
                'phrase_text': "We're borrowing from China to fund this",
                'category': 'Borrowing',
                'difficulty_level': 'classic',
                'description': "Foreign holders buy gilts with pounds they already earned. The UK creates pounds, it doesn't borrow them."
            },
            {
                'phrase_text': "Tax and spend policies will ruin us",
                'category': 'Taxation',
                'difficulty_level': 'classic',
                'description': "For currency issuers, the sequence is spend and tax. Government spending creates the income that can be taxed."
            },
            {
                'phrase_text': "There's no money left",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "A currency-issuing government always has its own currency available. Resource availability is the real constraint."
            },
            {
                'phrase_text': "We're on the road to ruin",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "Deficits are normal and necessary for a growing economy where the private sector desires to save."
            },
            {
                'phrase_text': "The government is drowning in debt",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "Government debt represents private sector savings. One sector's liability is another's asset."
            },
            {
                'phrase_text': "We need fiscal responsibility",
                'category': 'Deficit',
                'difficulty_level': 'classic',
                'description': "True fiscal responsibility means using policy space to achieve full employment and price stability, not arbitrary deficit targets."
            },
            {
                'phrase_text': "The burden on future taxpayers",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "There is no burden. Future government spending will provide the income from which future taxes are paid."
            },
            {
                'phrase_text': "We're heading for a debt crisis",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "Currency issuers with floating exchange rates and debt in their own currency cannot face debt crises."
            },
            {
                'phrase_text': "The government purse is empty",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Currency-issuing governments don't have purses that can be empty. They create currency when spending."
            },
            {
                'phrase_text': "Reckless spending will destroy the economy",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Spending beyond real resource capacity causes inflation. The amount of spending needed depends on economic conditions."
            },
            {
                'phrase_text': "We're stealing from our kids",
                'category': 'Intergenerational',
                'difficulty_level': 'classic',
                'description': "Investment today in infrastructure, education, and environment creates the prosperity our children will inherit."
            },
            {
                'phrase_text': "The government must stop spending money like water",
                'category': 'Spending',
                'difficulty_level': 'classic',
                'description': "Appropriate government spending depends on economic capacity, not arbitrary financial limits. Underspending wastes resources."
            },
            {
                'phrase_text': "We're broke as a nation",
                'category': 'Debt',
                'difficulty_level': 'classic',
                'description': "Nations with sovereign currencies cannot be broke in their own currency. Real wealth is productive capacity, not money."
            },

            # ADVANCED DIFFICULTY (35 phrases)
            {
                'phrase_text': "The gilt market won't tolerate this level of borrowing",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "The Bank of England sets the base rate and can control the yield curve. Markets accommodate, they don't constrain."
            },
            {
                'phrase_text': "Bond vigilantes will punish this fiscal irresponsibility",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "The BoE's ability to purchase gilts and set rates means bond markets cannot force policy changes on the UK."
            },
            {
                'phrase_text': "This will crowd out private investment",
                'category': 'Spending',
                'difficulty_level': 'advanced',
                'description': "Government spending creates income and demand, typically crowding in private investment. Currency issuers don't compete for funds."
            },
            {
                'phrase_text': "The OBR forecasts show this is unsustainable",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "OBR forecasts use flawed assumptions about government budget constraints that don't apply to currency issuers."
            },
            {
                'phrase_text': "We'll end up like Greece",
                'category': 'Debt',
                'difficulty_level': 'advanced',
                'description': "Greece uses the euro and cannot issue its own currency. The UK issues pounds and faces completely different constraints."
            },
            {
                'phrase_text': "Interest payments on the debt are becoming unaffordable",
                'category': 'Debt',
                'difficulty_level': 'advanced',
                'description': "The government that issues the currency can always make interest payments in that currency. The BoE can also set rates."
            },
            {
                'phrase_text': "The deficit to GDP ratio is too high",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "This ratio is descriptive, not prescriptive. The appropriate deficit depends on private sector saving desires and economic capacity."
            },
            {
                'phrase_text': "We need to restore confidence in the UK's public finances",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "Market confidence follows policy outcomes, not arbitrary fiscal rules. Full employment and stability create genuine confidence."
            },
            {
                'phrase_text': "This will trigger capital flight",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "Appropriate policy that achieves growth and stability attracts capital. The exchange rate is a policy variable, not a constraint."
            },
            {
                'phrase_text': "The markets are demanding fiscal consolidation",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "Markets respond to economic fundamentals. Premature consolidation that weakens the economy creates genuine market concerns."
            },
            {
                'phrase_text': "We're approaching the limits of fiscal space",
                'category': 'Spending',
                'difficulty_level': 'advanced',
                'description': "Fiscal space for a currency issuer is determined by inflation risk and real resources, not financial constraints."
            },
            {
                'phrase_text': "The Treasury can't fund these commitments",
                'category': 'Spending',
                'difficulty_level': 'advanced',
                'description': "The Treasury, through the BoE, credits accounts electronically. The question is whether real resources exist to fulfill commitments."
            },
            {
                'phrase_text': "Gilt yields are rising, proving the markets are worried",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "Rising yields may reflect growth expectations or inflation expectations. The BoE can control yields through asset purchases if needed."
            },
            {
                'phrase_text': "We need to protect our credit rating",
                'category': 'Debt',
                'difficulty_level': 'advanced',
                'description': "Credit ratings are irrelevant for currency issuers who cannot default on obligations in their own currency."
            },
            {
                'phrase_text': "The debt servicing costs are spiralling",
                'category': 'Debt',
                'difficulty_level': 'advanced',
                'description': "The government and central bank determine interest rates on government debt. These are policy choices, not market impositions."
            },
            {
                'phrase_text': "We'll face a sovereign debt crisis like the eurozone",
                'category': 'Debt',
                'difficulty_level': 'advanced',
                'description': "The UK issues its own currency with a floating exchange rate. Eurozone countries use a foreign currency (the euro)."
            },
            {
                'phrase_text': "Quantitative easing has reached its limits",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "QE is just asset swaps that change portfolio composition. The real constraint is inflation, not operational limits."
            },
            {
                'phrase_text': "The structural deficit is too large",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "The structural deficit calculation embeds flawed assumptions about potential output and incorrectly treats deficits as problematic per se."
            },
            {
                'phrase_text': "We need to reduce our reliance on foreign creditors",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "Foreign gilt holders already earned pounds through trade. The UK doesn't rely on them for currency it issues itself."
            },
            {
                'phrase_text': "This spending will debase the currency",
                'category': 'Inflation',
                'difficulty_level': 'advanced',
                'description': "Currency value depends on what it can purchase. Appropriate spending that mobilizes idle resources doesn't cause inflation."
            },
            {
                'phrase_text': "The fiscal multiplier is too low to justify this spending",
                'category': 'Spending',
                'difficulty_level': 'advanced',
                'description': "Multipliers are higher when slack exists. They describe secondary effects, not the primary case for mobilizing idle resources."
            },
            {
                'phrase_text': "We're exceeding our fiscal rules",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "Fiscal rules are self-imposed political constraints, not economic necessities. They should serve policy goals, not constrain them arbitrarily."
            },
            {
                'phrase_text': "The government needs to pre-fund its spending commitments",
                'category': 'Spending',
                'difficulty_level': 'advanced',
                'description': "Currency-issuing governments spend by crediting accounts. They cannot pre-fund in a currency they create."
            },
            {
                'phrase_text': "We're becoming dependent on Bank of England financing",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "The BoE and Treasury are both government. Coordination between monetary and fiscal authorities is normal, not problematic dependence."
            },
            {
                'phrase_text': "The current account deficit makes this borrowing dangerous",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "Current account deficits reflect trade flows. They don't constrain domestic currency creation or government's ability to spend."
            },
            {
                'phrase_text': "We're monetizing the debt",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "This phrase implies a constraint that doesn't exist. Government spending is always money creation for a currency issuer."
            },
            {
                'phrase_text': "The automatic stabilizers are already overstretched",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "Automatic stabilizers are functioning as designed. Their cost reflects economic weakness, not government profligacy."
            },
            {
                'phrase_text': "We need to front-load fiscal consolidation",
                'category': 'Austerity',
                'difficulty_level': 'advanced',
                'description': "Premature consolidation during weak demand destroys jobs and income, typically worsening the deficit through reduced tax revenue."
            },
            {
                'phrase_text': "The cyclically adjusted deficit is the real concern",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "Cyclical adjustment embeds contestable assumptions about potential output and wrongly treats deficits as inherently problematic."
            },
            {
                'phrase_text': "This will trigger a run on sterling",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "Exchange rates float. Appropriate policy that achieves domestic goals is more important than defending arbitrary exchange rate levels."
            },
            {
                'phrase_text': "We're facing a funding crisis",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "Currency-issuing governments don't face funding crises in their own currency. They create the currency in which they spend."
            },
            {
                'phrase_text': "The debt to GDP trajectory is explosive",
                'category': 'Debt',
                'difficulty_level': 'advanced',
                'description': "This ratio conflates stocks and flows. The denominator grows with appropriate spending, and currency issuers face no solvency constraint."
            },
            {
                'phrase_text': "We must maintain fiscal credibility with the markets",
                'category': 'Deficit',
                'difficulty_level': 'advanced',
                'description': "True credibility comes from achieving full employment and price stability, not adhering to arbitrary fiscal rules that undermine these goals."
            },
            {
                'phrase_text': "The gilt strike proves we've lost market confidence",
                'category': 'Borrowing',
                'difficulty_level': 'advanced',
                'description': "The BoE can always ensure gilt auctions clear by setting appropriate rates or purchasing gilts directly if needed."
            },
            {
                'phrase_text': "This level of stimulus will overheat the economy",
                'category': 'Spending',
                'difficulty_level': 'advanced',
                'description': "Overheating requires spending beyond productive capacity. With unemployment and slack, appropriate spending mobilizes idle resources."
            },

            # TECHNICAL DIFFICULTY (25 phrases)
            {
                'phrase_text': "The debt sustainability analysis shows this is untenable",
                'category': 'Debt',
                'difficulty_level': 'technical',
                'description': "DSA frameworks designed for currency users don't apply to currency issuers. Sustainability is about inflation, not solvency."
            },
            {
                'phrase_text': "The r minus g dynamic is becoming unfavorable",
                'category': 'Debt',
                'difficulty_level': 'technical',
                'description': "This framework assumes government solvency constraint. For currency issuers, inflation risk matters, not the r-g relationship."
            },
            {
                'phrase_text': "We're breaching the fiscal compact requirements",
                'category': 'Deficit',
                'difficulty_level': 'technical',
                'description': "The fiscal compact is a eurozone political agreement that reflected flawed economics. It doesn't apply to the UK and embeds false constraints."
            },
            {
                'phrase_text': "The intertemporal budget constraint is being violated",
                'category': 'Debt',
                'difficulty_level': 'technical',
                'description': "Currency issuers don't face intertemporal budget constraints. They face inflation constraints based on real resource availability."
            },
            {
                'phrase_text': "Ricardian equivalence means this spending won't stimulate demand",
                'category': 'Spending',
                'difficulty_level': 'technical',
                'description': "Ricardian equivalence requires unrealistic assumptions. Empirically, government spending does affect aggregate demand."
            },
            {
                'phrase_text': "The monetary financing prohibition must be respected",
                'category': 'Borrowing',
                'difficulty_level': 'technical',
                'description': "All government spending is monetary financing. The prohibition is a political convention, not an economic necessity."
            },
            {
                'phrase_text': "The zero lower bound constrains our options",
                'category': 'Borrowing',
                'difficulty_level': 'technical',
                'description': "Fiscal policy remains fully effective at the ZLB. Monetary policy constraints actually argue for more fiscal space use."
            },
            {
                'phrase_text': "The primary balance needs urgent correction",
                'category': 'Deficit',
                'difficulty_level': 'technical',
                'description': "Primary balance targets are arbitrary. The appropriate balance depends on private sector saving desires and resource utilization."
            },
            {
                'phrase_text': "The seigniorage revenue is insufficient",
                'category': 'Borrowing',
                'difficulty_level': 'technical',
                'description': "Seigniorage is a red herring for currency issuers. Government spending doesn't depend on seigniorage revenue."
            },
            {
                'phrase_text': "The fiscal impulse is procyclical",
                'category': 'Spending',
                'difficulty_level': 'technical',
                'description': "This observation may be true but reflects policy failure, not necessity. Fiscal policy should be countercyclical to stabilize demand."
            },
            {
                'phrase_text': "The output gap estimates don't support this spending",
                'category': 'Spending',
                'difficulty_level': 'technical',
                'description': "Output gap estimates are highly uncertain and embed contestable assumptions. Unemployment is a better guide to resource slack."
            },
            {
                'phrase_text': "We're violating the Taylor rule prescription",
                'category': 'Inflation',
                'difficulty_level': 'technical',
                'description': "The Taylor rule is a monetary policy guideline, not fiscal. Coordinated policy using all tools achieves better outcomes than mechanical rules."
            },
            {
                'phrase_text': "The fiscal theory of the price level suggests this causes inflation",
                'category': 'Inflation',
                'difficulty_level': 'technical',
                'description': "FTPL has theoretical problems and mixed empirical support. Inflation depends on spending relative to productive capacity."
            },
            {
                'phrase_text': "The NAIRU is being exceeded by this employment policy",
                'category': 'Spending',
                'difficulty_level': 'technical',
                'description': "The NAIRU is a flawed concept with unstable estimates. A Job Guarantee can achieve full employment with price stability."
            },
            {
                'phrase_text': "The Maastricht criteria are being breached",
                'category': 'Deficit',
                'difficulty_level': 'technical',
                'description': "Maastricht criteria were designed for eurozone currency users. The UK issues pounds and faces different constraints."
            },
            {
                'phrase_text': "The fiscal anchor is being abandoned",
                'category': 'Deficit',
                'difficulty_level': 'technical',
                'description': "True fiscal anchors are full employment and price stability, not arbitrary deficit or debt targets that undermine these goals."
            },
            {
                'phrase_text': "The debt feedback loop is becoming unstable",
                'category': 'Debt',
                'difficulty_level': 'technical',
                'description': "Feedback loop concerns assume solvency risk. Currency issuers face inflation risk, which is managed through appropriate policy settings."
            },
            {
                'phrase_text': "The marginal propensity to consume from deficit spending is too low",
                'category': 'Spending',
                'difficulty_level': 'technical',
                'description': "This focuses on secondary effects. The primary purpose is mobilizing unemployed resources, not maximizing MPC."
            },
            {
                'phrase_text': "The IS-LM framework shows this is pushing up interest rates",
                'category': 'Borrowing',
                'difficulty_level': 'technical',
                'description': "IS-LM assumes government funding constraints. With sovereign currency, the central bank sets rates as a policy choice."
            },
            {
                'phrase_text': "The Phillips curve suggests this triggers wage-price spiral",
                'category': 'Inflation',
                'difficulty_level': 'technical',
                'description': "The Phillips curve relationship is unstable. With resource slack, appropriate spending doesn't trigger inflation. Job Guarantee provides price anchor."
            },
            {
                'phrase_text': "The ex ante fiscal stance is too expansionary",
                'category': 'Deficit',
                'difficulty_level': 'technical',
                'description': "Fiscal stance should respond to economic conditions. What appears expansionary may be appropriate given private sector saving desires."
            },
            {
                'phrase_text': "The contingent liabilities aren't being properly accounted for",
                'category': 'Debt',
                'difficulty_level': 'technical',
                'description': "Government liabilities in its own currency are always payable. The question is whether accepting these liabilities serves public purpose."
            },
            {
                'phrase_text': "The sovereign risk premium is rising",
                'category': 'Borrowing',
                'difficulty_level': 'technical',
                'description': "Risk premiums on currency-issuer debt reflect inflation expectations, not default risk. The central bank can control yields if needed."
            },
            {
                'phrase_text': "The debt overhang will constrain future growth",
                'category': 'Debt',
                'difficulty_level': 'technical',
                'description': "Debt overhang applies to currency users. For currency issuers, what matters is whether past spending built productive capacity."
            },
            {
                'phrase_text': "The neutral rate of interest analysis suggests we're at capacity",
                'category': 'Inflation',
                'difficulty_level': 'technical',
                'description': "R-star estimates are highly uncertain and backward-looking. Unemployment and inflation data provide better real-time capacity signals."
            },
        ]

        # Create all phrases
        created_count = 0
        for phrase_data in phrases:
            BingoPhrase.objects.create(**phrase_data)
            created_count += 1

        # Count by difficulty
        classic_count = sum(1 for p in phrases if p["difficulty_level"] == "classic")
        advanced_count = sum(1 for p in phrases if p["difficulty_level"] == "advanced")
        technical_count = sum(1 for p in phrases if p["difficulty_level"] == "technical")

        self.message_user(
            request,
            f'Successfully loaded {created_count} Budget Day Bingo phrases! '
            f'Classic: {classic_count}, Advanced: {advanced_count}, Technical: {technical_count}. '
            f'(Deleted {deleted_count} old phrases first)',
            messages.SUCCESS
        )

    load_all_budget_phrases.short_description = "🎯 Load all Budget Day Bingo phrases (replaces existing)"


class BingoSquareInline(admin.TabularInline):
    """Inline admin for bingo squares"""
    model = BingoSquare
    extra = 0
    readonly_fields = ['position', 'phrase', 'marked', 'marked_at']
    can_delete = False


@admin.register(BingoCard)
class BingoCardAdmin(admin.ModelAdmin):
    """Bingo card admin"""
    list_display = ['id', 'user', 'difficulty', 'completed', 'marked_count', 'completion_time', 'generated_at']
    list_filter = ['difficulty', 'completed', 'generated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['user', 'difficulty', 'generated_at', 'completion_time']
    inlines = [BingoSquareInline]

    def marked_count(self, obj):
        return f"{obj.marked_count}/{obj.total_squares}"
    marked_count.short_description = 'Progress'


@admin.register(BingoSquare)
class BingoSquareAdmin(admin.ModelAdmin):
    """Bingo square admin"""
    list_display = ['id', 'card', 'phrase', 'position', 'marked', 'marked_at']
    list_filter = ['marked', 'auto_detected']
    search_fields = ['phrase__phrase_text', 'card__user__username']
    readonly_fields = ['card', 'phrase', 'position']
