''''

short tall keywords  # value|truncatechars:9

python manage.py createsuperuser

pip freeze > requirements.txt

if request.method == "POST":
    test_empty_order-namn = request.POST['order-namn']
    test_empty_order-efternamn = request.POST['order-efternamn']
    test_empty_order-epost = request.POST['order-epost']
    test_empty_order-adress = request.POST['order-adress']

    if testempty_order-namn =="" or test_empty_order-efternamn =="" or test_empty_order-epost=="" or  test_empty_order-adress == "" :
        messages.warning(request,"there is one or more fields are empty!")
        return redirect("your page you want to redirect")



        import re

def extract_clinic_categories(pdf_file):
    with open(pdf_file, 'rb') as f:
        text = f.read().decode('utf-8')

    clinic_categories = re.findall(r'\b(Dentist|Heart|Skin)\b', text)

    return clinic_categories

def format_clinic_categories(clinic_categories):
    tuples = []
    for clinic_category in clinic_categories:
        tuple = (clinic_category, _('{}'.format(clinic_category)))
        tuples.append(tuple)

    return tuples

if __name__ == '__main__':
    tuples = format_clinic_categories(extract_clinic_categories('clinic_categories.pdf'))

    print(tuples)

'''
