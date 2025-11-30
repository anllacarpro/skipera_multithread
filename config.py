# https://github.com/serv0id/skipera

BASE_URL = "https://www.coursera.org/api/"
GRAPHQL_URL = "https://www.coursera.org/graphql-gateway"

PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
PERPLEXITY_MODEL = "sonar-pro"  # adjust this according to your preference

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
    'x-coursera-application': 'ondemand',
    'x-coursera-version': '3bfd497de04ae0fef167b747fd85a6fbc8fb55df',
    'x-requested-with': 'XMLHttpRequest',
}

COOKIES = {
    '__204u': '3854574651-1744423556093',
    '__stripe_mid': 'd67fc8dd-a937-41ab-85b7-198664a853c20e6a4a',
    'drift_aid': '262f80ef-4636-487d-80b2-9bda1cd1797d',
    'driftt_aid': '262f80ef-4636-487d-80b2-9bda1cd1797d',
    'profileconsent': 'eyIxNjQ0NDg3NDIiOnsiY2NwYVJlcXVpcmVkIjpmYWxzZSwiZ2RwclJlcXVpcmVkIjpmYWxzZX19',
    'CAUTH': 'InnDGwgJzDJho5RQ-tO6PmOuD1CgAEkXxt5wJE7uJ7d9bzS6fNcALMdme92ve3zK2XoYAmau_xxZaLYuMqs2vQ.1lbLPw3W3Sp2i6DXrXQQMA.or4hFxW2tp9ZfYjbSCRoS2apkspz_pkibHjzrfNdEtnDaBWp5Oy2gRP0fUjD8zz0HvwZMnAIzkdCzmWEfwJ23YVGKIM-6Uo3whggG05Qvx2UhTLecFK0jwVlIyVM7MbIjjo1c2yW3gz9zND1r56cbnNYQHE8XkgvXKVAEZ34KrEGUOBYW6XPSSm7_VSH2Sdoywrj6SurYP6FqBE7pgtW9chHCv_JGJlWF7DQznKHByDiDs2vicR2JKvz9zty4kEvmQH3azlW9kvjfB2Nr1U4atsH9mZpniLN0x3GDGe_g9loj46ESu5SlhFlE_AWgClEuo1xvcQlQBxSOfsUkBbT9BstljnfVmomh57Rju5nTOz65fvyG0XzRshoMCujtB69cb1J2z1TM7czPVA5freMT_MiuIjuRosdWVJg5O8YRH6JvDfxMonEhT_pXD0NAdh1oQP2FJGE_S32sVszZyGo4WQ08z6MUZfo3TB0NlEe3g0',
    'CSRF3-Token': '1765203010.W3voFYOnhOYmfxVX',
    '__400v': '91da05b5-e354-4bf1-a589-c895d2619314',
    '__400vt': '1764530853512',
}

# Credentials
PERPLEXITY_API_KEY = "REDACTED"
