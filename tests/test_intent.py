"""
Unit tests for ghost_audit/intent.py.
Validates multilingual request intent classification and NOT_APPLICABLE detection.
"""

import unittest

from ghost_audit.intent import classify_request_intent, is_deletion_request


class TestRequestIntent(unittest.TestCase):
    def test_english_deletion_phrases(self):
        t1 = "Please permanently delete the account associated with this email address."
        res1 = classify_request_intent(t1)
        self.assertEqual(res1.intent, "DELETION")
        self.assertTrue(is_deletion_request(t1))

        t2 = "Please erase the account linked to this email address."
        self.assertEqual(classify_request_intent(t2).intent, "DELETION")

        t3 = "Please close my account and process the associated personal-data deletion."
        self.assertEqual(classify_request_intent(t3).intent, "DELETION")

    def test_multilingual_deletion_phrases(self):
        # Portuguese
        t_pt = "Solicito a exclusão permanente da conta associada a este e-mail."
        self.assertEqual(classify_request_intent(t_pt).intent, "DELETION")

        # Spanish
        t_es = "Solicito la eliminación permanente de la cuenta asociada a este correo."
        self.assertEqual(classify_request_intent(t_es).intent, "DELETION")

        # French
        t_fr = "Je demande la suppression définitive du compte associé à cette adresse e-mail."
        self.assertEqual(classify_request_intent(t_fr).intent, "DELETION")

        # German
        t_de = "Bitte löschen Sie das mit dieser E-Mail-Adresse verknüpfte Konto."
        self.assertEqual(classify_request_intent(t_de).intent, "DELETION")

        # Korean
        t_ko = "이 이메일과 연결된 계정을 삭제해 주십시오."
        self.assertEqual(classify_request_intent(t_ko).intent, "DELETION")

    def test_non_deletion_not_applicable_phrases(self):
        # Access
        t_acc = "Can you tell me what personal information you hold about me? This is an information request, not a request to erase it."
        res_acc = classify_request_intent(t_acc)
        self.assertEqual(res_acc.intent, "NON_DELETION")
        self.assertFalse(is_deletion_request(t_acc))

        # Copy / Export
        t_exp = "I need a copy of last year's invoices for my records. Please leave my profile and purchase history in place."
        self.assertEqual(classify_request_intent(t_exp).intent, "NON_DELETION")

        # Portability download
        t_dl = "I'd like to download my account information in a portable format. Please keep the account as it is."
        self.assertEqual(classify_request_intent(t_dl).intent, "NON_DELETION")

        # Correction
        t_cor = "My surname is misspelled on the account. Can you correct it without removing any of my records?"
        self.assertEqual(classify_request_intent(t_cor).intent, "NON_DELETION")

        # Opt-out
        t_opt = "Please stop the promotional emails. I still need the account and my order history, so I am not asking for deletion."
        self.assertEqual(classify_request_intent(t_opt).intent, "NON_DELETION")

        # Support
        t_sup = "I can't access my profile and need help resetting the login. Do not close the account."
        self.assertEqual(classify_request_intent(t_sup).intent, "NON_DELETION")

    def test_empty_text_flags_manual_review(self):
        res = classify_request_intent("")
        self.assertTrue(res.is_manual_review)


if __name__ == "__main__":
    unittest.main()
