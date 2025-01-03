PGDMP  0                    |            attendancedbb    15.8    16.4 /    4           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            5           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            6           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            7           1262    16959    attendancedbb    DATABASE     �   CREATE DATABASE attendancedbb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'English_Indonesia.1252';
    DROP DATABASE attendancedbb;
                postgres    false            �            1255    16960    check_absence()    FUNCTION     1  CREATE FUNCTION public.check_absence() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    last_absence TIMESTAMP;
    blocking_duration INTERVAL;
BEGIN
    -- Ambil durasi blocking dari pengaturan global
    SELECT setting_value::INT * INTERVAL '1 minute' INTO blocking_duration
    FROM global_settings
    WHERE setting_key = 'blocking_duration_minutes';

    RAISE NOTICE 'Durasi blocking: %', blocking_duration;

    -- Periksa apakah region diizinkan
    IF NOT EXISTS (
        SELECT 1
        FROM region
        WHERE id = NEW.region_id AND (
            allowed = TRUE OR 
            (allowed = FALSE AND 
             NEW.region_id = (SELECT region_id FROM employee WHERE id_karyawan = NEW.id_karyawan))
        )
    ) THEN
        RAISE EXCEPTION 'Karyawan tidak diizinkan untuk absen di region ini.';
    END IF;

    -- Memeriksa waktu absensi terakhir di region yang sama
    SELECT check_in INTO last_absence
    FROM absensi
    WHERE id_karyawan = NEW.id_karyawan AND region_id = NEW.region_id
    ORDER BY check_in DESC
    LIMIT 1;

    RAISE NOTICE 'Absensi terakhir: %', last_absence;

    -- Jika ada catatan absensi terakhir, periksa jarak waktunya
    IF last_absence IS NOT NULL THEN
        IF NEW.check_in - last_absence < blocking_duration THEN
            RAISE NOTICE 'Waktu tersisa untuk blocking: %', blocking_duration - (NEW.check_in - last_absence);
            RAISE EXCEPTION 'Karyawan sudah absen dalam durasi blocking di region ini.';
        END IF;
    END IF;

    -- Lanjutkan proses jika tidak ada masalah
    RETURN NEW;
END;
$$;
 &   DROP FUNCTION public.check_absence();
       public          postgres    false            �            1255    16961    check_region()    FUNCTION     o	  CREATE FUNCTION public.check_region() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    last_absence TIMESTAMP;
    last_region_id INT;
    registered_region_id INT;  -- Menyimpan region yang terdaftar untuk karyawan
    is_allowed BOOLEAN;         -- Untuk mencatat izin akses
    blocking_duration INT;      -- Durasi waktu blokir (dalam menit)
BEGIN
    -- Ambil nilai blocking_duration_minutes dari tabel global_settings
    SELECT setting_value INTO blocking_duration
    FROM global_settings
    WHERE setting_key = 'blocking_duration_minutes';

    -- Ubah setting_value menjadi integer
    blocking_duration := CAST(blocking_duration AS INTEGER);

    RAISE NOTICE 'Region ID: %', NEW.region_id;

    -- Ambil region yang terdaftar untuk karyawan
    SELECT region_id INTO registered_region_id
    FROM employee
    WHERE id_karyawan = NEW.id_karyawan;

    -- Cek apakah region diizinkan untuk semua karyawan (allowed = true)
    SELECT allowed INTO is_allowed
    FROM region
    WHERE id = NEW.region_id;

    -- Jika region diizinkan untuk semua karyawan
    IF is_allowed THEN
        RETURN NEW;  -- Izinkan absensi di semua region
    END IF;

    -- Jika region tidak diizinkan untuk semua karyawan, cek apakah karyawan terdaftar di region yang sesuai
    IF registered_region_id IS NOT NULL AND registered_region_id = NEW.region_id THEN
        RETURN NEW;  -- Izinkan absensi jika karyawan terdaftar di region tersebut
    END IF;

    -- Jika tidak memenuhi kondisi di atas, batalkan absensi
    RAISE EXCEPTION 'Karyawan tidak diizinkan untuk absen di region ini.';
    
    -- Memeriksa waktu absensi terakhir dan region terakhir
    SELECT check_in, region_id INTO last_absence, last_region_id
    FROM absensi
    WHERE id_karyawan = NEW.id_karyawan
    ORDER BY check_in DESC
    LIMIT 1;

    -- Jika ada absensi terakhir
    IF last_absence IS NOT NULL THEN
        -- Cek apakah region terakhir sama dengan region baru
        IF last_region_id = NEW.region_id THEN
            -- Jika sudah absen di region yang sama dalam waktu kurang dari durasi blocking
            IF NOW() - last_absence < INTERVAL '1 minute' * blocking_duration THEN
                RAISE EXCEPTION 'Absen sudah dilakukan di region ini dalam waktu % menit terakhir.', blocking_duration;
            END IF;
        END IF;
    END IF;

    RETURN NEW; -- Mengizinkan data untuk masuk ke database
END;
$$;
 %   DROP FUNCTION public.check_region();
       public          postgres    false            �            1255    16962    prevent_early_reattendance()    FUNCTION     .  CREATE FUNCTION public.prevent_early_reattendance() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    last_absence TIMESTAMP;
    last_region_id INT;
    blocking_duration INT;
BEGIN
    -- Ambil durasi blokir dari pengaturan global
    SELECT setting_value INTO blocking_duration
    FROM global_settings 
    WHERE setting_key = 'blocking_duration_minutes';

    IF blocking_duration IS NULL THEN
        -- Jika tidak ditemukan, defaultkan ke 10 menit
        blocking_duration := 10;
    END IF;

    -- Memeriksa waktu absensi terakhir dan region terakhir
    SELECT check_in, region_id INTO last_absence, last_region_id
    FROM absensi
    WHERE id_karyawan = NEW.id_karyawan
    ORDER BY check_in DESC
    LIMIT 1;

    -- Jika ada absensi terakhir
    IF last_absence IS NOT NULL THEN
        -- Cek apakah region terakhir sama dengan region baru
        IF last_region_id = NEW.region_id THEN
            -- Jika sudah absen di region yang sama dalam waktu kurang dari durasi yang ditentukan
            IF NOW() - last_absence < INTERVAL '1 minute' * blocking_duration THEN
                RAISE EXCEPTION 'Karyawan sudah absen dalam %s menit terakhir di region ini.', blocking_duration;
            END IF;
        END IF;
    END IF;

    RETURN NEW; -- Mengizinkan data untuk masuk ke database
END;
$$;
 3   DROP FUNCTION public.prevent_early_reattendance();
       public          postgres    false            �            1259    16963    absensi    TABLE     �   CREATE TABLE public.absensi (
    id integer NOT NULL,
    id_karyawan integer,
    check_in timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    photo text,
    region_id integer,
    nama character varying(255)
);
    DROP TABLE public.absensi;
       public         heap    postgres    false            �            1259    16969    absensi_id_seq    SEQUENCE     �   CREATE SEQUENCE public.absensi_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 %   DROP SEQUENCE public.absensi_id_seq;
       public          postgres    false    214            8           0    0    absensi_id_seq    SEQUENCE OWNED BY     A   ALTER SEQUENCE public.absensi_id_seq OWNED BY public.absensi.id;
          public          postgres    false    215            �            1259    16970    employee    TABLE     K  CREATE TABLE public.employee (
    id_karyawan integer NOT NULL,
    name character varying(255) NOT NULL,
    face_encoding bytea,
    photo text[],
    status character(1) DEFAULT 'A'::bpchar,
    tgl_create timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    create_by character varying(255),
    tgl_update timestamp without time zone,
    update_by character varying(255),
    tgl_delete timestamp without time zone,
    delete_by character varying(255),
    region_id integer,
    CONSTRAINT employee_status_check CHECK ((status = ANY (ARRAY['A'::bpchar, 'N'::bpchar])))
);
    DROP TABLE public.employee;
       public         heap    postgres    false            �            1259    16978    employee_id_karyawan_seq    SEQUENCE     �   CREATE SEQUENCE public.employee_id_karyawan_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 /   DROP SEQUENCE public.employee_id_karyawan_seq;
       public          postgres    false    216            9           0    0    employee_id_karyawan_seq    SEQUENCE OWNED BY     U   ALTER SEQUENCE public.employee_id_karyawan_seq OWNED BY public.employee.id_karyawan;
          public          postgres    false    217            �            1259    17040    global_settings    TABLE     �   CREATE TABLE public.global_settings (
    setting_key character varying(255) NOT NULL,
    setting_value character varying(255) NOT NULL
);
 #   DROP TABLE public.global_settings;
       public         heap    postgres    false            �            1259    16979    region    TABLE     �   CREATE TABLE public.region (
    id integer NOT NULL,
    name character varying NOT NULL,
    allowed boolean DEFAULT false,
    is_active boolean DEFAULT true
);
    DROP TABLE public.region;
       public         heap    postgres    false            �            1259    16986    region_id_seq    SEQUENCE     �   CREATE SEQUENCE public.region_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 $   DROP SEQUENCE public.region_id_seq;
       public          postgres    false    218            :           0    0    region_id_seq    SEQUENCE OWNED BY     ?   ALTER SEQUENCE public.region_id_seq OWNED BY public.region.id;
          public          postgres    false    219            �            1259    16987    users    TABLE     P  CREATE TABLE public.users (
    id integer NOT NULL,
    nama character varying NOT NULL,
    username character varying(50) NOT NULL,
    password character varying(255) NOT NULL,
    role character varying(20) NOT NULL,
    CONSTRAINT role_check CHECK (((role)::text = ANY (ARRAY[('super_admin'::character varying)::text, ('admin'::character varying)::text, ('karyawan'::character varying)::text]))),
    CONSTRAINT users_role_check CHECK (((role)::text = ANY (ARRAY[('super_admin'::character varying)::text, ('admin'::character varying)::text, ('karyawan'::character varying)::text])))
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    16994    users_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 #   DROP SEQUENCE public.users_id_seq;
       public          postgres    false    220            ;           0    0    users_id_seq    SEQUENCE OWNED BY     =   ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;
          public          postgres    false    221            {           2604    16995 
   absensi id    DEFAULT     h   ALTER TABLE ONLY public.absensi ALTER COLUMN id SET DEFAULT nextval('public.absensi_id_seq'::regclass);
 9   ALTER TABLE public.absensi ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    215    214            }           2604    16996    employee id_karyawan    DEFAULT     |   ALTER TABLE ONLY public.employee ALTER COLUMN id_karyawan SET DEFAULT nextval('public.employee_id_karyawan_seq'::regclass);
 C   ALTER TABLE public.employee ALTER COLUMN id_karyawan DROP DEFAULT;
       public          postgres    false    217    216            �           2604    16997 	   region id    DEFAULT     f   ALTER TABLE ONLY public.region ALTER COLUMN id SET DEFAULT nextval('public.region_id_seq'::regclass);
 8   ALTER TABLE public.region ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    219    218            �           2604    16998    users id    DEFAULT     d   ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);
 7   ALTER TABLE public.users ALTER COLUMN id DROP DEFAULT;
       public          postgres    false    221    220            )          0    16963    absensi 
   TABLE DATA           T   COPY public.absensi (id, id_karyawan, check_in, photo, region_id, nama) FROM stdin;
    public          postgres    false    214   3L       +          0    16970    employee 
   TABLE DATA           �   COPY public.employee (id_karyawan, name, face_encoding, photo, status, tgl_create, create_by, tgl_update, update_by, tgl_delete, delete_by, region_id) FROM stdin;
    public          postgres    false    216   'R       1          0    17040    global_settings 
   TABLE DATA           E   COPY public.global_settings (setting_key, setting_value) FROM stdin;
    public          postgres    false    222   8a       -          0    16979    region 
   TABLE DATA           >   COPY public.region (id, name, allowed, is_active) FROM stdin;
    public          postgres    false    218   ra       /          0    16987    users 
   TABLE DATA           C   COPY public.users (id, nama, username, password, role) FROM stdin;
    public          postgres    false    220   �a       <           0    0    absensi_id_seq    SEQUENCE SET     >   SELECT pg_catalog.setval('public.absensi_id_seq', 764, true);
          public          postgres    false    215            =           0    0    employee_id_karyawan_seq    SEQUENCE SET     F   SELECT pg_catalog.setval('public.employee_id_karyawan_seq', 6, true);
          public          postgres    false    217            >           0    0    region_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.region_id_seq', 6, true);
          public          postgres    false    219            ?           0    0    users_id_seq    SEQUENCE SET     ;   SELECT pg_catalog.setval('public.users_id_seq', 13, true);
          public          postgres    false    221            �           2606    17000    absensi absensi_pkey 
   CONSTRAINT     R   ALTER TABLE ONLY public.absensi
    ADD CONSTRAINT absensi_pkey PRIMARY KEY (id);
 >   ALTER TABLE ONLY public.absensi DROP CONSTRAINT absensi_pkey;
       public            postgres    false    214            �           2606    17002    employee employee_pkey 
   CONSTRAINT     ]   ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_pkey PRIMARY KEY (id_karyawan);
 @   ALTER TABLE ONLY public.employee DROP CONSTRAINT employee_pkey;
       public            postgres    false    216            �           2606    17046 $   global_settings global_settings_pkey 
   CONSTRAINT     k   ALTER TABLE ONLY public.global_settings
    ADD CONSTRAINT global_settings_pkey PRIMARY KEY (setting_key);
 N   ALTER TABLE ONLY public.global_settings DROP CONSTRAINT global_settings_pkey;
       public            postgres    false    222            �           2606    17004    region region_pkey 
   CONSTRAINT     P   ALTER TABLE ONLY public.region
    ADD CONSTRAINT region_pkey PRIMARY KEY (id);
 <   ALTER TABLE ONLY public.region DROP CONSTRAINT region_pkey;
       public            postgres    false    218            �           2606    17006    users users_pkey 
   CONSTRAINT     N   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    220            �           2606    17008    users users_username_key 
   CONSTRAINT     W   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);
 B   ALTER TABLE ONLY public.users DROP CONSTRAINT users_username_key;
       public            postgres    false    220            �           2620    17009    absensi check_absence_trigger    TRIGGER     {   CREATE TRIGGER check_absence_trigger BEFORE INSERT ON public.absensi FOR EACH ROW EXECUTE FUNCTION public.check_absence();
 6   DROP TRIGGER check_absence_trigger ON public.absensi;
       public          postgres    false    214    235            �           2620    17010    absensi check_early_attendance    TRIGGER     �   CREATE TRIGGER check_early_attendance BEFORE INSERT ON public.absensi FOR EACH ROW EXECUTE FUNCTION public.prevent_early_reattendance();
 7   DROP TRIGGER check_early_attendance ON public.absensi;
       public          postgres    false    214    234            �           2620    17011    absensi check_region_trigger    TRIGGER     y   CREATE TRIGGER check_region_trigger BEFORE INSERT ON public.absensi FOR EACH ROW EXECUTE FUNCTION public.check_region();
 5   DROP TRIGGER check_region_trigger ON public.absensi;
       public          postgres    false    214    236            �           2620    17047 *   absensi prevent_early_reattendance_trigger    TRIGGER     �   CREATE TRIGGER prevent_early_reattendance_trigger BEFORE INSERT ON public.absensi FOR EACH ROW EXECUTE FUNCTION public.prevent_early_reattendance();
 C   DROP TRIGGER prevent_early_reattendance_trigger ON public.absensi;
       public          postgres    false    234    214            �           2620    17013    absensi validate_region    TRIGGER     t   CREATE TRIGGER validate_region BEFORE INSERT ON public.absensi FOR EACH ROW EXECUTE FUNCTION public.check_region();
 0   DROP TRIGGER validate_region ON public.absensi;
       public          postgres    false    214    236            �           2606    17014     absensi absensi_id_karyawan_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.absensi
    ADD CONSTRAINT absensi_id_karyawan_fkey FOREIGN KEY (id_karyawan) REFERENCES public.employee(id_karyawan) ON DELETE CASCADE;
 J   ALTER TABLE ONLY public.absensi DROP CONSTRAINT absensi_id_karyawan_fkey;
       public          postgres    false    214    216    3210            �           2606    17019    absensi absensi_region_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.absensi
    ADD CONSTRAINT absensi_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.region(id);
 H   ALTER TABLE ONLY public.absensi DROP CONSTRAINT absensi_region_id_fkey;
       public          postgres    false    218    3212    214            �           2606    17024     employee employee_region_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.employee
    ADD CONSTRAINT employee_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.region(id);
 J   ALTER TABLE ONLY public.employee DROP CONSTRAINT employee_region_id_fkey;
       public          postgres    false    3212    216    218            )   �  x����j]7����b��iNҬ��@)����i�ƥ�������L�^�.�I�WN�2��?�b�D'�$��ܓ�oZ7�$f$rJ�~|�<>�������Ǉ������ϗ�ׇ�_/O�<�?���ħ��5����kR�\c�"�j��6�O�T��60}��eJ\������fn�TY�������/��>�s����������q�n�����h?�,��%7/%�i=x��a���-i�D�4PiÏH�Zk�(U*o�I)��Q�MTj(��j'��kh;�e�R�Y�nme�h�Z5����DE�'"�bA�剪H����.��2@���Ȁ�æұ�߸(�
c�e�f5l|�鋺�pJ&ׅ�.�����lM�S=8Q٘�p�W9����˟�F^9�� ;�G�LKT�����=�ȶ��3g����HExo1d�?$F-rL0?�����{u�V�E�G�Q0�4�6��� ����[!��V�I~��f����gڛ�^�f�����w'z9]�)�u`z��V���L�1"
�#�[��&�>6�����-�ɻ��řy��L�]=�p]3SF��鲧W��	Z����60ݎL�}�T�,ڢ,1yd���`���<��5w
�pdB�ԍ1zBa͟40)OL�Lt'��5o��	��.�dȦH��u`J����j,;�ǰ�H�J�����RFuR]�/?dҾ5e{N���Y9��o!��V���k��g���%���N�n71�"Iͣ�_5�fd�Ƙ��h%d���Zg�u"��e�9Ԑ�o��\��J:0�񆰛blh$;�g&&��@��1G;y|����&3D���s����LFO�Їk�x�S���zޙ���1G;�wF&R���K,F����)�J}�?2K�� 癜�MpџUo2�	����ʴ�LIh���:���i	�ʴ6�&f��tĨTY���9ƽߚ�=�b�l�&ӱ� A���L(�`~6����ob��h�s��7�c��&!���F��%Qc��\j7�LM�q,��\E����s���}�fW�Xb
���.F�gov&'/�B�iy�����T
�����7ѝS#]�62Ǡ3��3Ւ�z��,���ŷ�u�[aZ[�F;�"��{/�;������<�B�$ve�Y)������bB�4�bB�[��{��ް��-�<�:�xYi��ݕ<Vl��X"�1D����Ģ�m6�э1ّ541�o0k?�6�ӥp�Κ�K��%���!�X���9��H�R-U��w����Q���J>1�H�$� �Ǖ�̔�h�x_4�� l(�M�;38f$�̲�)d�D:����s�u�α!\����LHn�u?i�کSz[J�Q�N����Rb1�I��C��gپ�1Ec�f�������T�'dW�����!<2e~��~@v�%$j�!ꪳ/�}#������,��չ�Y���l�621�,5��W#�+?PT��[�gMZ?���Kl��o1Y0���1��V&����!7�X،n"-q�����0��x��S�����(��      +     x��Z[�^��|�
����˼�$���&�(HlCv,�߷8����x�0�G�Hg/���&����Ϗ��?~�o����o�k�PfJ��a���k[=��v=-��S�i�w�Y/m��~��=X}mq[����⩗Yf~mQ�����v+��mW�W��Cl	��,���7��x}�Fȯ=�3{h�m��Z������>fC������~��η%t�`�J
C��������֑�z��#���5���}MC���y)�hԷ�ɶ����[˗�)��i~�/�1�އ�
����I_޷���>�I5����r�T�����{��y㯻b__:vD�>�o���e���w��g�L␜��{{��J���Y�j�G����oп�zC�i���*qV���=L��̴�6~׭�z�ap�8����>�J~{�K���$I��;Zl����h��k��Vj�}=9&�_g�bo�i��N�|=k�"��k��N��6�"�=k����s�R�w�&��o���b>�����w�n?��az�����I��؟�!>�}��e�}�B��wc�K��l���ݾZB�H�Ӱ���o&#{_T�x� uU�ޟ��M|�'��x��R�x�t��x����-y<�y����g�=V�߱4���s��/�������f)��i"�'ŷƨ��xS��GY/X��=������Ys��wX���b������s)�3W|A�[Z|?V�$����V�n�=*�?�A����s��O�,�p��|�C����J�����IB�!c ǟ�M_���B(^�ɋ�/xG�g�z��/}�˭��Ϲº��R���,��Tٿ�m��VW��`3^b�7%�����G���Z���oK�w���xo�W�y~��'b�������^��?�o>Y)>�Hrf��	�~�ﯞ��O���߾2�?�2��0����o���o��&����O{=���?}�ϧ�?%����N�}/y������=O����>��^jy�)�߷���w�=����������22��2�ԕ������
E�;�����o����7�O��o1Oo?B���`Q��bˎQp���R����1�
�_\7�Q�-p�E�M�q_����`G��#�Adὕ��	һ���id�!{���%���"��:>���9���r����5N]�[v�KD�Jnς�g�߇�"'����U$3��;���/د��.�?$är��������s�~X,Yh�2c5JFR.[��}����/���-��.޿����x�p�A��b�4o6�5��<��$>z�eR2��d2AK����z�Jr�UBZ�NN�TI=>7z4�����EE�m>��K�XB*t�o�7���~��/�M��Ap}'ov�i���.z$o�rU�OѴ=�A��+y��q�{��E�4-�c��󁿂�tZo\u	���N�w�3e'O�W(1���	�+�1��K޿�u�/ީ������=��F�r1r\�8D&�"�',&�G�Y�}��u|�p�F%1ܶF��i#��_�K��ib��+�]L�0��F�Gߢ,N�w��v��7Q!��ϯ�:X���=����bL^Ԓ�/���ȿ����{��n�>5#=W�W�z������~4p+�Ow���
�w1��*�oD�R�ɋ�O&�3#ޘ|�[+�g2���}fPz�9�Ϳ����u��|��%��RfKD����K�R~I�O�ɼo�;���?����Q��������G�A>}����.�q�:�����\eb���3��I8�-b�znq��0�_���D&���J�{1�f�ˁ���кH�[�b���B��8�I\�7/!�3�����\��zV��WxR!+)�	�l�ß���s~jJjnO|z�P��E󟺍�v@�cD��=�_ʹImT�B�o(q��0*iVR!�י�����l�Մ��]$��,^��pn�$�K9�\��R���r�c�-l��ܣ��y>H�Q(	��R�2b`.2%Snk�! l�7WP�%!��߱�p#pK����tx��Fp%�N���|AU���� �J���=��uFh+ʝv�|�.��������ܢ�$����`ڊ�����N/��R,F��G�{2�Yo��T��Zʢ\�;�UtV*^f���������*���}����f^^��V������ƹ�5���6T�v�m.򟨹	i�v�
������rAan�6�ϧY%.$ཽq����H�h�]�>� ����I�)�&}�zAU��e���g����Y��H;ą���Z��o�8&��MҚp.cm�#���Dq+\ �s��mtP�lL.|ձ�Q!51~�6���-�!?P��WTҶ��9)�o4�f�?����OP���ٴ+�K|u����~�0�����gv�Xz��c~��%������/%��+K�7���k��jh|���XQ�L�Н���}Fa����$yS����2*���,B�����G]�M��@�csEY����S��+r�0:�<�4�
��K��\�]�P��+<X?8�P6b�l�^��`�Ӹby1q�q≪�b�R��5��4W���Pa� �O�U[7G�0H$_V�QHQ�f���D�0���wQ?<��Қ�΋.��|���d�Ҁ�^q��9�?o��X嚣8�j��p�ovOϨ��_�[�e�[�� �84�*.7Bٿ���e1���Jg�iM�}b��xk�=����[���k�U�*���+h�*nȢW�S�7���h�?R�CE��b�Ϙφ�x�C���>t�#�_C�[��+!���q��-:��!��qvbQ�:A�	�����-���wN����^M��.�%�����pTڏ������, ];]G��!�gՕ����y�8-ץ�����N��Kr{C�������"X�&�?nI3����CE잗x<`c����E�}���DbR��[�Xcz
�%URm���zN�
,�uD� �I���^�TѿM�-��X`�����QE�]�@,���Ń��Y�J�H�t��A��%���J8�>�����b�Xu��Ko���'���7�����Zl����Z�W�֞���W���E+��%ȵQJ�ox���F.~] 	qWYTtn�1���
 �
)H�jT�kqo�ӻ�)���Y ��C:%<��^BT�J���I�gN�S� �&���_�[��p�RZ#x�SvQ�86��8����S4���0����9j!�E߰)0W#�����ٳ���FM�	;Q�{��T���t.i���k�h$��_r ^���\�ZoiG�r�:Ծ�>)j�VS"]��|(�	�x4�Bh�v8e`r�>��4�����LJ	Z�$!歫.�v�Br�=���2�q�:�̇ܖCa	��0��J��������Q<,Px���ώ|�r��~������#<A�|�	�mz{L)AA�!+���Ɨ0⺥`�������N*4�\��p�I�nM�)i~q��)�^�ȑo4^NjT/��(�tI7��*[���({T_V⃄qj�K$:!���/HA2�_�~񡌇C��_ �<~Pr%�%�����he	{	�x\���^!��uP��g�W��䃐����1��z$�T��?��P<��Ϻ�t��X��W�ʅ��O4�g���K�/�q�A����(>�|h�K�T�i��k�_�Y���\��� F�6LW$�⃈���G]������6�c��^o�՗��mn����w�<�{�� ���      1   *   x�K��O���K�O)-J,��ϋ���+-I-�44������ ��      -   8   x�3�JM���S0�L�,�2�q��\��ļ��< '��&g�3�ɕ 91z\\\ L�      /   p  x���[O�@ǟ˧��r�>c����"+n61s�m��
|����&��p2gfr��s��/����ѨxJ��ˁ~��/�2���m�E1�ˢ���# �e���&�y�Ԏ�U<l���t����,��j7~��8��v��5�u�,� �A��U�%� ��&l�g�D��N��E|���N&����<_���(���M��s;�T�u����DKF/zGc_�:O��q^/>Ȯ��|��k��	���aR�~2)����:h�0�0R�S
�1�{0�c��Y##��� $���7 %�:һ�K��Y�X����7��G{̰К1�!�hm0�SZ`�)u��@:&e a4��� YCA� 5�Hځ�A:�-��f�P:��/��qn�W�i�4�6L�6�Y�(��s�0�J$<5�QK<}AQ��K}������v~t11ygս�c&y�"i �N�j�B��)���\E�tB�o#0�h�hS.%�yp�(���|���L�����wzs*�i
���J�Q�n5�:�HSBN-� $�!8��{'!ͤ���`��'�P�n�k���zz��{3���]1��}�{w�=�W�i�_���*ݞd3uS�7ſǭV��PFY     