from cronjobs.itau.credit_card import Entry


def test_business_and_installment():
    assert Entry._business_and_installment('COMPRA CREDITO') == ('COMPRA CREDITO', None)
    assert Entry._business_and_installment('COMPRA CREDITO         ') == ('COMPRA CREDITO', None)
    assert Entry._business_and_installment('COMPRA CREDITO (1/2)') == ('COMPRA CREDITO', '1/2')
    assert Entry._business_and_installment('COMPRA CREDITO (01/02)') == ('COMPRA CREDITO', '01/02')
    assert Entry._business_and_installment('COMPRA CREDITO (01/02)') == ('COMPRA CREDITO', '01/02')
    assert Entry._business_and_installment('COMPRA CREDITO 1/2') == ('COMPRA CREDITO', '1/2')
    assert Entry._business_and_installment('COMPRA CREDITO  (01/02)  ') == (
        'COMPRA CREDITO', '01/02'
    )
