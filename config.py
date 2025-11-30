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
    'CAUTH': "wncf886clXvk3fBns-CIN1Ye6V7JIlzefEY_RriLWvRrT-vajhu3WS_0FT-CdwO6hBJ86TrrMP8DRYaO-6heEQ.gRW_sBVmel30Hcmd1uCpXA.oYnC3eFb-IGSCYjq5YTzRPHdBrebNFEk-Ha3dThvSBB8vysOR4KHt-t0OW1v_FnrlhtbWdALRUprps2lwe5onfU41oAIP1VHSsm-ltCp69icm1OB5w1F_AsrFVHOpqY_oUolRSLgVeIOmwxFaWjP8FevdWtVTPNNNT24aF83DkRMSWzZLyD9EILbMgGyigUAFt3yoJ8pyG7Bh3nY33FhTxPxIob3Cv9kce1l5-tO_kGJwQ0SPnTcVxOIrEf0u5zRH8wOBF4FgFoT7SMO_GB7e9dFgHPf0l1-uTIh2we_VdKOY1vsD45YbaLIEif4Gpqggh1NhRokcavBBflWKcqlrsdYlOu7TZD0pfrI8s9LAD5IQ3yypxiQ8myxaOdxBdu0CMACh_0AbFSHfeVZWJEcKe-B8KW1D4Gjgg9qt_HHWRP9n1qGYxyaocSX6Igo-AM6_QaP_0iBvTdXimBT6TgveDGAGjr-0W3XoUviZR1vXUxJ4fRdfGt-4T0S_CvS26Kp",
    '__204u': '5649102421-1763657736189',
    '__400v': 'a4f11185-2651-4b55-8b65-724f96960eda',
    '__204v': '6bd0c5fa-88ea-41b3-865e-de6346524126',
    '__400vt': '1764513222280',
    '_ga': 'GA1.1.1893998923.1763657743',
    '_ga_7GZ59JSFWQ': 'GS2.1.s1764513210$o10$g0$t1764513210$j60$l0$h319423629',
    'FPID': "FPID2.2.ht7Gooh4bgfTjjE02OgcJHg267MgRMaPkdWoWShoQUw%3D.1742240447",
    'FPLC': "zxfz2hJUnUcvhSlAVmUnPWz4jfLwZ%2BxDOyJh%2B9DxdM5AlX3HOk%2FZ0I6via2i2POmAOn%2B8EegO2ZTwx2SGVqhHgLYIu1W%2FhAvW1ywEDO%2BnMPwnSafHKfpfNzjRpwjug%3D%3D",
    'CSRF3-Token' : '1765213458.gaXd1A2NEY4Rku17',
}
# Credentials
import os

# Prefer reading the Perplexity API key from an environment variable to
# avoid committing secrets to the repository. Set `PERPLEXITY_API_KEY`
# in your environment or export it before running the tool:
#
# PowerShell:
#   $env:PERPLEXITY_API_KEY = 'your_key_here'
#
#PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
# Gemini (Google) settings - optional. If you set `GEMINI_API_KEY`, the
# solver will prefer Gemini for answering quizzes.
# PowerShell:
#   $env:GEMINI_API_KEY = 'your_gemini_api_key'
#   $env:GEMINI_MODEL = 'gemini-1.5'  # optional
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta2/models")
