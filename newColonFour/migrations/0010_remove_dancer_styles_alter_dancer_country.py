# Generated by Django 4.2.14 on 2024-07-30 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("newColonFour", "0009_remove_battle_host_battle_host"),
    ]

    operations = [
        migrations.RemoveField(model_name="dancer", name="styles",),
        migrations.AlterField(
            model_name="dancer",
            name="country",
            field=models.CharField(
                choices=[
                    ("🇺🇸", "United States"),
                    ("🇨🇦", "Canada"),
                    ("🇲🇽", "Mexico"),
                    ("🇬🇹", "Guatemala"),
                    ("🇭🇹", "Haiti"),
                    ("🇧🇿", "Belize"),
                    ("🇨🇷", "Costa Rica"),
                    ("🇸🇻", "El Salvador"),
                    ("🇭🇳", "Honduras"),
                    ("🇳🇮", "Nicaragua"),
                    ("🇵🇦", "Panama"),
                    ("🇨🇺", "Cuba"),
                    ("🇩🇴", "Dominican Republic"),
                    ("🇯🇲", "Jamaica"),
                    ("🇧🇸", "Bahamas"),
                    ("🇧🇧", "Barbados"),
                    ("🇹🇹", "Trinidad and Tobago"),
                    ("🇬🇧", "United Kingdom"),
                    ("🇫🇷", "France"),
                    ("🇩🇪", "Germany"),
                    ("🇮🇹", "Italy"),
                    ("🇪🇸", "Spain"),
                    ("🇵🇹", "Portugal"),
                    ("🇳🇱", "Netherlands"),
                    ("🇧🇪", "Belgium"),
                    ("🇨🇭", "Switzerland"),
                    ("🇦🇹", "Austria"),
                    ("🇸🇪", "Sweden"),
                    ("🇳🇴", "Norway"),
                    ("🇩🇰", "Denmark"),
                    ("🇫🇮", "Finland"),
                    ("🇮🇸", "Iceland"),
                    ("🇮🇪", "Ireland"),
                    ("🇵🇱", "Poland"),
                    ("🇨🇿", "Czech Republic"),
                    ("🇸🇰", "Slovakia"),
                    ("🇭🇺", "Hungary"),
                    ("🇷🇴", "Romania"),
                    ("🇧🇬", "Bulgaria"),
                    ("🇬🇷", "Greece"),
                    ("🇹🇷", "Turkey"),
                    ("🇷🇺", "Russia"),
                    ("🇺🇦", "Ukraine"),
                    ("🇧🇾", "Belarus"),
                    ("🇱🇹", "Lithuania"),
                    ("🇱🇻", "Latvia"),
                    ("🇪🇪", "Estonia"),
                    ("🇲🇹", "Malta"),
                    ("🇨🇾", "Cyprus"),
                    ("🇱🇺", "Luxembourg"),
                    ("🇲🇨", "Monaco"),
                    ("🇱🇮", "Liechtenstein"),
                    ("🇸🇲", "San Marino"),
                    ("🇦🇩", "Andorra"),
                    ("🇻🇦", "Vatican City"),
                    ("🇷🇸", "Serbia"),
                    ("🇲🇪", "Montenegro"),
                    ("🇲🇰", "North Macedonia"),
                    ("🇦🇱", "Albania"),
                    ("🇧🇦", "Bosnia and Herzegovina"),
                    ("🇽🇰", "Kosovo"),
                    ("🇸🇮", "Slovenia"),
                    ("🇭🇷", "Croatia"),
                ],
                max_length=3,
            ),
        ),
    ]