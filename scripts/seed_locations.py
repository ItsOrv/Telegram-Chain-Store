from src.core.database import SessionLocal
from src.core.models import Province, City

def seed_locations():
    db = SessionLocal()
    try:
        # Add Provinces
        provinces = [
            "Tehran", "Isfahan", "Alborz", "Fars", "Khorasan Razavi", "East Azerbaijan",
            "West Azerbaijan", "Gilan", "Mazandaran", "Kermanshah", "Khuzestan", "Sistan and Baluchestan",
            "Kerman", "Hormozgan", "Lorestan", "Markazi", "Qom", "Qazvin", "Semnan", "Golestan",
            "Ardabil", "Zanjan", "Ilam", "Bushehr", "Chaharmahal and Bakhtiari", "South Khorasan",
            "North Khorasan", "Kohgiluyeh and Boyer-Ahmad", "Hamedan", "Yazd"
        ]
        
        province_objects = [Province(name=province) for province in provinces]
        db.add_all(province_objects)
        db.commit()

        # Add Cities
        cities = [
            # Tehran Province
            City(name="Tehran", province_id=province_objects[0].id),
            City(name="Rey", province_id=province_objects[0].id),
            City(name="Shemiranat", province_id=province_objects[0].id),
            City(name="Varamin", province_id=province_objects[0].id),
            # Isfahan Province
            City(name="Isfahan", province_id=province_objects[1].id),
            City(name="Kashan", province_id=province_objects[1].id),
            City(name="Najafabad", province_id=province_objects[1].id),
            City(name="Shahin Shahr", province_id=province_objects[1].id),
            # Alborz Province
            City(name="Karaj", province_id=province_objects[2].id),
            City(name="Nazarabad", province_id=province_objects[2].id),
            City(name="Savojbolagh", province_id=province_objects[2].id),
            City(name="Taleqan", province_id=province_objects[2].id),
            # Fars Province
            City(name="Shiraz", province_id=province_objects[3].id),
            City(name="Marvdasht", province_id=province_objects[3].id),
            City(name="Jahrom", province_id=province_objects[3].id),
            City(name="Fasa", province_id=province_objects[3].id),
            # Khorasan Razavi Province
            City(name="Mashhad", province_id=province_objects[4].id),
            City(name="Neyshabur", province_id=province_objects[4].id),
            City(name="Sabzevar", province_id=province_objects[4].id),
            City(name="Torbat-e Heydarieh", province_id=province_objects[4].id),
            # East Azerbaijan Province
            City(name="Tabriz", province_id=province_objects[5].id),
            City(name="Maragheh", province_id=province_objects[5].id),
            City(name="Marand", province_id=province_objects[5].id),
            City(name="Ahar", province_id=province_objects[5].id),
            # West Azerbaijan Province
            City(name="Urmia", province_id=province_objects[6].id),
            City(name="Khoy", province_id=province_objects[6].id),
            City(name="Mahabad", province_id=province_objects[6].id),
            City(name="Miandoab", province_id=province_objects[6].id),
            # Gilan Province
            City(name="Rasht", province_id=province_objects[7].id),
            City(name="Anzali", province_id=province_objects[7].id),
            City(name="Lahijan", province_id=province_objects[7].id),
            City(name="Astara", province_id=province_objects[7].id),
            # Mazandaran Province
            City(name="Sari", province_id=province_objects[8].id),
            City(name="Babol", province_id=province_objects[8].id),
            City(name="Amol", province_id=province_objects[8].id),
            City(name="Qaem Shahr", province_id=province_objects[8].id),
            # Kermanshah Province
            City(name="Kermanshah", province_id=province_objects[9].id),
            City(name="Eslamabad-e Gharb", province_id=province_objects[9].id),
            City(name="Sarpol-e Zahab", province_id=province_objects[9].id),
            City(name="Kangavar", province_id=province_objects[9].id),
            # Khuzestan Province
            City(name="Ahvaz", province_id=province_objects[10].id),
            City(name="Abadan", province_id=province_objects[10].id),
            City(name="Dezful", province_id=province_objects[10].id),
            City(name="Behbahan", province_id=province_objects[10].id),
            # Sistan and Baluchestan Province
            City(name="Zahedan", province_id=province_objects[11].id),
            City(name="Chabahar", province_id=province_objects[11].id),
            City(name="Zabol", province_id=province_objects[11].id),
            City(name="Iranshahr", province_id=province_objects[11].id),
            # Kerman Province
            City(name="Kerman", province_id=province_objects[12].id),
            City(name="Rafsanjan", province_id=province_objects[12].id),
            City(name="Sirjan", province_id=province_objects[12].id),
            City(name="Bam", province_id=province_objects[12].id),
            # Hormozgan Province
            City(name="Bandar Abbas", province_id=province_objects[13].id),
            City(name="Minab", province_id=province_objects[13].id),
            City(name="Bandar Lengeh", province_id=province_objects[13].id),
            City(name="Qeshm", province_id=province_objects[13].id),
            # Lorestan Province
            City(name="Khorramabad", province_id=province_objects[14].id),
            City(name="Borujerd", province_id=province_objects[14].id),
            City(name="Dorud", province_id=province_objects[14].id),
            City(name="Aligudarz", province_id=province_objects[14].id),
            # Markazi Province
            City(name="Arak", province_id=province_objects[15].id),
            City(name="Saveh", province_id=province_objects[15].id),
            City(name="Khomein", province_id=province_objects[15].id),
            City(name="Mahallat", province_id=province_objects[15].id),
            # Qom Province
            City(name="Qom", province_id=province_objects[16].id),
            # Qazvin Province
            City(name="Qazvin", province_id=province_objects[17].id),
            City(name="Takestan", province_id=province_objects[17].id),
            City(name="Abyek", province_id=province_objects[17].id),
            City(name="Buin Zahra", province_id=province_objects[17].id),
            # Semnan Province
            City(name="Semnan", province_id=province_objects[18].id),
            City(name="Shahroud", province_id=province_objects[18].id),
            City(name="Damghan", province_id=province_objects[18].id),
            City(name="Garmsar", province_id=province_objects[18].id),
            # Golestan Province
            City(name="Gorgan", province_id=province_objects[19].id),
            City(name="Gonbad-e Kavus", province_id=province_objects[19].id),
            City(name="Aliabad-e Katul", province_id=province_objects[19].id),
            City(name="Bandar-e Torkaman", province_id=province_objects[19].id),
            # Ardabil Province
            City(name="Ardabil", province_id=province_objects[20].id),
            City(name="Parsabad", province_id=province_objects[20].id),
            City(name="Meshgin Shahr", province_id=province_objects[20].id),
            City(name="Germi", province_id=province_objects[20].id),
            # Zanjan Province
            City(name="Zanjan", province_id=province_objects[21].id),
            City(name="Abhar", province_id=province_objects[21].id),
            City(name="Khodabandeh", province_id=province_objects[21].id),
            City(name="Khorramdarreh", province_id=province_objects[21].id),
            # Ilam Province
            City(name="Ilam", province_id=province_objects[22].id),
            City(name="Dehloran", province_id=province_objects[22].id),
            City(name="Mehran", province_id=province_objects[22].id),
            City(name="Abdanan", province_id=province_objects[22].id),
            # Bushehr Province
            City(name="Bushehr", province_id=province_objects[23].id),
            City(name="Borazjan", province_id=province_objects[23].id),
            City(name="Bandar Ganaveh", province_id=province_objects[23].id),
            City(name="Khormoj", province_id=province_objects[23].id),
            # Chaharmahal and Bakhtiari Province
            City(name="Shahr-e Kord", province_id=province_objects[24].id),
            City(name="Borujen", province_id=province_objects[24].id),
            City(name="Farsan", province_id=province_objects[24].id),
            City(name="Lordegan", province_id=province_objects[24].id),
            # South Khorasan Province
            City(name="Birjand", province_id=province_objects[25].id),
            City(name="Qaen", province_id=province_objects[25].id),
            City(name="Ferdows", province_id=province_objects[25].id),
            City(name="Nehbandan", province_id=province_objects[25].id),
            # North Khorasan Province
            City(name="Bojnord", province_id=province_objects[26].id),
            City(name="Shirvan", province_id=province_objects[26].id),
            City(name="Esfarayen", province_id=province_objects[26].id),
            City(name="Maneh and Samalqan", province_id=province_objects[26].id),
            # Kohgiluyeh and Boyer-Ahmad Province
            City(name="Yasuj", province_id=province_objects[27].id),
            City(name="Dehdasht", province_id=province_objects[27].id),
            City(name="Gachsaran", province_id=province_objects[27].id),
            City(name="Likak", province_id=province_objects[27].id),
            # Hamedan Province
            City(name="Hamedan", province_id=province_objects[28].id),
            City(name="Malayer", province_id=province_objects[28].id),
            City(name="Nahavand", province_id=province_objects[28].id),
            City(name="Asadabad", province_id=province_objects[28].id),
            # Yazd Province
            City(name="Yazd", province_id=province_objects[29].id),
            City(name="Ardakan", province_id=province_objects[29].id),
            City(name="Mehriz", province_id=province_objects[29].id),
            City(name="Taft", province_id=province_objects[29].id)
        ]
        db.add_all(cities)
        db.commit()

        print("Location data seeded successfully!")

    except Exception as e:
        print(f"Error seeding locations: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_locations()
