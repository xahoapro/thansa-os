"""Reviewed release registrations for exact native-profile qualification evidence.

Keys bind platform, binary/version, SDK and the complete profile source hash.
Values are SHA-256 of actual qualification evidence retained with the release.
This host source is the registration authority, deliberately outside the profile
hash to avoid a self-referential digest. No environment/HTTP/model can register a
profile. Add an entry only after its native black-box qualification has passed;
changing profile source invalidates the entry. Historical receipts stay readable.
"""
from __future__ import annotations

import re

# Reviewed path-independent release closures. Registration is external authority,
# deliberately excluded from its own source/manifest fingerprint. Empty until
# the complete production pipeline has passed actual qualification.
# Key: (platform, CLI version/hash, SDK version, profile version/hash, fingerprint).
# Value: SHA-256 of retained reviewed qualification evidence.
REVIEWED_RELEASES = {}

# Reviewed candidates may be exercised only by the separate local-dummy
# QualificationSession. This is not live profile registration or account
# readiness. Same exact seven-part key; value pins the candidate review evidence.
# Remains empty until a final candidate closure has been independently reviewed.
REVIEWED_QUALIFICATION_CANDIDATES = {}

# Exact dummy-auth/native enforcement evidence; this does not attest account
# readiness, actual call usage, business quality or final eligibility.
# docs/superpowers/evidence/2026-10-23-m2c-native-qualification.json
QUALIFIED_PROFILES = {('win32', '2.1.308',
    'c9796ba22a9221586b36371b36f5b66198d66eb4badf6a4cf4a5f7b07becea53', '0.2.116',
    'claude-isolated-roles-v2', '9dcf718470e70957d07454bb8b50fbde79575a3b23d8c06e24cc9b749051116b'):
    '98ee4e8c406091ee84db2862cbf80b11a5f15cf88f7d4d96188d5e2360822ea7',
    # Exact paired-view/solver/typed-role/native-lifetime enforcement, local dummy providers.
    # docs/superpowers/evidence/2026-10-23-m2d1-native-qualification-final.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '4d346a3ae4f1afa99784fc51307258ad99a8d470ac6a0c46f1d330e6b0e656fa'):
    '6b48a371a095854a65c73ae349b2a10c52bced005e46354f85eccb3988e831ec',
    # Exact changed semantic-outcome footprint, same native runtime and full enforcement suites.
    # docs/superpowers/evidence/2026-10-23-m2d1-native-qualification-outcome.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '958527ac69c3b5728044b22cf6d3bdebb920da7cbe46a9da261e899568ced1ef'):
    '3ecdaa284b5adba1a3a5664d6b879bfb42b8d8644e998f90ae8e2eccb16b1199',
    # Exact raw-artifact prompt footprint, same native runtime; all20 enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-format.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'e7aaa5bd9902860e440349f0654f2a6ec92271770030f8bfaf6a0d584efb2a60'):
    'fe554b9c61888815fce5d2f75b9b2d9e8b86549be0d055778517e051db173ac7',
    # Exact bounded read-only CLI-observation footprint, all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-observation.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', 'be4a5866a411fdcbb68bc7728d6cec9418fac19132ca4a46dce40ac1cb45ca0b'):
    'bca02de04db6c69b216a4526266dc77cf37736b61d654ddcbd8f97e9d9646867',
    # Exact preparation-heartbeat footprint; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-preparation-heartbeat.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '972175a29309295afc596902ef711ea51400ba77c2f39e27aab1141f9a0f6a10'):
    '216d1ee93bcd4430ac9a1e097125c0e6ac20da5795c1bb1aa293c5afaf56a922',
    # Exact83-source versioned skill-read footprint; all20 local native checks.
    # docs/superpowers/evidence/2026-10-24-m2d1-native-qualification-skill-reads.json
    ('win32', '2.1.309',
    '5441781f2b6bbd07354b4a74560ee88c68c9bf05d6db3c7e24c452c91673dc53', '0.2.116',
    'claude-isolated-roles-v2', '04c8c77baec04d04019752bc8abc2f9a5906e094ededfbdd56cfc3c712aef126'):
    '8feb58acc6112a292b2b5c1b575d53bee384e51d8177b35761107904eea27c63',
    # Final 0.314.0 source (M2D1 integrated, M2E activation schema), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m2-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'ee73f81305f01f7c1b43ed72744c9c2abf22ceff04b1661f60e48fd058273acd'):
    'a09564b7178629ddee37aa91094a14fd4e8fa21931925d45c4e7f85e12e6625b',
    # M3 source (canary schema 12 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m3-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '7849768b28e6793a033d7126f8780256f66bb6ce2e98b864e71eeffc9820f837'):
    '4145f0da8292669f392b37c685b8baa465e8f39bbee2998b60b8fabed5564f8b',
    # M4 source (routing schema 13 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m4-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '1a8a08a07394d0ab31ecab33eeed216b8b971c0d0ed0d8a5a42b131c72f3f0c1'):
    '50effe17018e1a0d7525f6b29c21ee8492f863e3e56d6c58d57589f6ea11544d',
    # M5 source (agent procedure schema 14 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-25-m5-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'c509f9a1560d3c93631c38ad1a461d5a5430f3149cf20ab51724fab6bfd6ed19'):
    'a54ac57fde4d0fab32d8301aee740c3645e686b11c0fc43298d4bebbdfeff6bb',
    # M6 source (bundle schema 15 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m6-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', 'b609a52ac28ea3d8837b74b7738ee3fd5c45b9d16169bb8564ed3b7f423da403'):
    'a76f2c044455b43fb627d34cb590163cb8577f6cfb9f65607f490628718f79cb',
    # M7 source (team schema 16 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m7-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '3c5543a3c14634b3736b51eb278b7c7f805554e3ab59ac8a908772230151d1f5'):
    '072ee94994ac9737d3bc06492d7e672cb944035719d22321adbd7baa5402abea',
    # M8 source (library schema 17 in the store footprint), CLI 2.1.310; all20 native enforcement checks.
    # docs/superpowers/evidence/2026-10-26-m8-native-qualification-cli310.json
    ('win32', '2.1.310',
    'f9a3920634ae3b961ee92c2eb58d0051f5f8852b120983d0a4f57b6a5efeba61', '0.2.116',
    'claude-isolated-roles-v2', '34a52a7243750ec0f797930cd633b9915e82dd1e7b8ce4c3e4f5b06efeb53099'):
    '85a0341e174aea2fd3e55ee154090d6d1c6564efff9f4e4e46cf7ea532decb4d'}


def profile_qualification(pin, platform):
    key = (platform, pin["cli_version"], pin["cli_hash"], pin["sdk_version"],
           pin["profile_version"], pin["profile_hash"])
    evidence = QUALIFIED_PROFILES.get(key)
    return evidence if type(evidence) is str and re.fullmatch(r"[0-9a-f]{64}", evidence) else None
