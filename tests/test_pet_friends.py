from api import PetFriends
from settings import valid_email, valid_password, big_name, symbol_type, invalid_key
import os

pf = PetFriends()

#_____________________________________Ниже дополнительные тесты из ДЗ_________________________________________________

def test_get_api_key_for_invalid_user(email="ddsfdsfeeeeeesd@gmail.com", password="dsfdsfsd"):
    """ Проверяем что запрос api ключа с некорректной почтой и паролем не вернет статус 200
    и в результате не содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Проверяем что статус ответа равен 403, и что ответ не содержит ключ
    assert status == 403
    assert 'key' not in result

def test_get_all_pets_with_invalid_key(filter=''):
    """ Проверяем что запрос всех питомцев с невалидным ключом не вернет статус 200 и список питомцев
    Доступное значение параметра filter - 'my_pets' либо '' """

    # Указываем невалидный ключ
    auth_key = invalid_key

    status, result = pf.get_list_of_pets(auth_key, filter)

    # Проверяем что статус ответа равен 403, и что ответ не содержит список питомцев
    assert status == 403
    assert 'pets' not in result

def test_add_new_pet_with_incorrect_data(name='', animal_type='', age='', pet_photo='images/45435.jpg'):
    """Проверяем что нельзя добавить питомца с неуказанным именем, породой и возрастом"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
    assert result['name'] != name


def test_add_new_pet_with_invalid_key(name='Барбариcкин', animal_type='двортерьер',
                                     age='2', pet_photo='images/45435.jpg'):
    """Проверяем что нельзя добавить питомца с невалидным ключом"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Указываем невалидный ключ
    auth_key = invalid_key

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Проверяем что статус ответа равен 403 и имя питомца не содержится в ответе
    assert status == 403
    assert name not in result


def test_add_new_pet_with_invalid_photo(name='Бар', animal_type='двортерьер',
                                     age='2', pet_photo='images/test_txt.txt'):
    """Проверяем что нельзя добавить питомца с некорректным форматом фото"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400
    assert result['name'] != name

def test_delete_self_pet_with_invalid_key():
    """Проверяем что нельзя удалить питомца используя невалидный ключ"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/45435.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Указываем невалидный ключ
    auth_key = invalid_key

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)
    
    # Ещё раз берем id первого питомца из списка
    pet_id2 = my_pets['pets'][0]['id']
    
    # Проверяем что статус ответа равен 403 и питомец не удалился
    assert status == 403
    assert pet_id == pet_id2

def test_try_delete_not_my_pet():
    """Проверяем что нельзя удалить чужого питомца"""

    # Получаем ключ auth_key и запрашиваем список всех питомцев и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    _, all_pets = pf.get_list_of_pets(auth_key, filter='')

    # Если первый питомец из общего списка это не мой питомец
    if all_pets['pets'][0]['id'] != my_pets['pets'][0]['id']:

        # Берём id первого питомца из списка всех питомцев и отправляем запрос на удаление
        pet_id = all_pets['pets'][0]['id']
        status, _ = pf.delete_pet(auth_key, pet_id)

        # Ещё раз запрашиваем список всех питомцев
        _, all_pets = pf.get_list_of_pets(auth_key, filter='')

        # Проверяем что статус ответа не равен 200 и в списке питомцев остался питомец
        assert status != 200
        assert pet_id in all_pets.values()
    # Если первый питомец это мой питомец - вывести ошибку о том, что это мой питомец
    else:
        raise Exception("First pet is my pet")

def test_update_self_pet_info_with_incorrect_data(name=big_name, animal_type=symbol_type, age='dededddd'):
    """Проверяем что нельзя обновить информацию о питомце некорректными данными"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 400 и имя питомца не соответствует заданному
        assert status == 400
        assert result['name'] != name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_update_not_my_pet_info(name='тест', animal_type='тестовый', age='9'):
    """Проверяем что нельзя обновить информацию чужого питомца"""

    # Получаем ключ auth_key и запрашиваем список всех питомцев и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, all_pets = pf.get_list_of_pets(auth_key, filter='')
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если первый питомец из общего списка это не мой питомец
    if all_pets['pets'][0]['id'] != my_pets['pets'][0]['id']:
        # Берём имя первого питомца из списка всех питомцев до изменения
        name1 = all_pets['pets'][0]['name']
        # Берём id первого питомца из списка всех питомцев и пробуем обновить его имя, тип и возраст
        status, result = pf.update_pet_info(auth_key, all_pets['pets'][0]['id'], name, animal_type, age)

        # Ещё раз запрашиваем список всех питомцев и имя первого питомца
        _, all_pets = pf.get_list_of_pets(auth_key, filter='')
        name2 = all_pets['pets'][0]['name']
        # Проверяем что статус ответа не равен 200 и имя питомца не изменилось
        assert status != 200
        assert name1 == name2

    # Если первый питомец это мой питомец - вывести ошибку о том, что это мой питомец
    else:
        raise Exception("First pet is my pet")


def test_add_new_simple_pet_with_incorrcet_data(name=symbol_type, animal_type=big_name,
                                     age='sgsdggdsgdg'):
    """Проверяем что нельзя добавить простого питомца без фото с некорректными данными"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Проверяем что статус ответа = 400 и имя питомца не соответствует заданному
    assert status == 400
    assert result['name'] != name

def test_add_pet_photo_with_invalid_file(pet_photo='images/test_txt.txt'):
    """Проверяем что нельзя добавить фото питомцу невалидным файлом"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем добавить фото
    if len(my_pets['pets']) > 0:
        # Задаем переменную с указанием файла фото первого питомца из списка
        photo1 = my_pets['pets'][0]['pet_photo']
        # Добавлем невалидный фомат фото первому питомцу в списке
        status, result = pf.add_new_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)

        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        photo2 = my_pets['pets'][0]['pet_photo']
        # Проверяем что статус ответа = 400 и фото питомца не изменилось
        assert status == 400
        assert photo1 == photo2
    else:
        raise Exception("There is no my pets")



        

# __________________________Ниже тесты из модуля + два из ДЗ____________________________________________

def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='Барбарискин', animal_type='двортерьер',
                                     age='2', pet_photo='images/45435.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name

def test_successful_delete_self_pet():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/45435.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Мурзик', animal_type='Котэ', age='5'):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Еслди список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # если спиок питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")

def test_add_new_pet_without_photo(name='erwerer', animal_type='двортерьер',
                                     age='7'):
    """Проверяем что можно добавить питомца с корректными данными без фото"""

    # Запрашиваем ключ api и сохраняем в переменую auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name


def test_add_pet_photo(pet_photo='images/iewfefs.jpg'):
    """Проверяем что можно добавить фото питомцу"""

    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Задаем переменную с указанием имени первого питомца из списка
    name = my_pets['pets'][0]['name']

    # Если список не пустой, то пробуем добавить фото
    if len(my_pets['pets']) > 0:
        # Задаем переменную с указанием имени первого питомца из списка
        name = my_pets['pets'][0]['name']
        # Добавлем фото первому питомцу в списке
        status, result = pf.add_new_pet_photo(auth_key, my_pets['pets'][0]['id'], pet_photo)
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

        # Проверяем что статус ответа = 200 и имя измененного питомца соответствует изначальному
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")
