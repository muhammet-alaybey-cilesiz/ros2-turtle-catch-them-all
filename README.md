# 🐢 ROS 2 Turtle Catch Them All

Bu proje, ROS 2 mimarisi kullanılarak geliştirilmiş otonom bir "avcı-toplayıcı" kaplumbağa simülasyonudur. Turtlesim düğümü üzerinde çalışan sistem, rastgele konumlarda beliren hedefleri (food turtles) algılar, oransal kontrol (P-Controller) ile rotasını hesaplar ve hedefleri teker teker avlar.

## ⚙️ Sistem Mimarisi ve Özellikler

Proje, modüler bir yapıya sahip olup 4 ana paketten oluşmaktadır:

* **`robot_interfaces`**: Hedeflerin isim ve konum verilerini taşımak için özel olarak tasarlanmış (Custom Message) `FoodState` ve `FoodStateArray` mesaj tiplerini barındırır.
* **`turtle_spawner`**: Belirli zaman aralıklarıyla sahneye yeni hedefler (food) ekler. Ekrandaki hedeflerin güncel pozisyonlarını ve isimlerini `/food_turtle_poses` isimli topic üzerinden yayınlar.
* **`turtle_controller`**: Ana kaplumbağanın beynidir. Dinamik olarak en yakın hedefi hesaplar, hedefe olan açısal hatayı ve uzaklığı baz alarak `/turtle1/cmd_vel` üzerinden hız komutları (Twist) gönderir. Hedefe ulaşıldığında turtlesim'in `kill` servisini çağırarak hedefi sahneden siler.
* **`robot_bringup`**: Tüm sistemi ve node'ları tek bir komutla ayağa kaldıran Launch dosyalarını içerir.

## 🛠️ Kurulum (Installation)

Projeyi kendi ROS 2 çalışma alanınızda (workspace) çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

```bash
# Çalışma alanınızın src klasörüne gidin
cd ~/ros2_ws/src

# Repoyu klonlayın
git clone [https://github.com/muhammet-alaybey-cilesiz/ros2-turtle-catch-them-all.git](https://github.com/muhammet-alaybey-cilesiz/ros2-turtle-catch-them-all.git)

# Bağımlılıkları derleyin
cd ~/ros2_ws
colcon build

# Ortamı kaynaklandırın
source install/setup.bash
