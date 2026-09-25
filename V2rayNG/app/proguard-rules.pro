
# ---- aoray fork: needed because R8 is now switched on -------------------
-keepattributes Signature, InnerClasses, EnclosingMethod, *Annotation*, RuntimeVisibleAnnotations, AnnotationDefault
# every config document is (de)serialised by Gson through field reflection
-keep class com.v2ray.ang.dto.** { *; }
-keep class com.v2ray.ang.dto { *; }
-keepclassmembers class * { @com.google.gson.annotations.SerializedName <fields>; }
-keep,allowobfuscation,allowshrinking class com.google.gson.reflect.TypeToken
-keep,allowobfuscation,allowshrinking class * extends com.google.gson.TypeAdapter
-keep,allowobfuscation,allowshrinking class * implements com.google.gson.TypeAdapterFactory
-keep,allowobfuscation,allowshrinking class * implements com.google.gson.JsonSerializer
-keep,allowobfuscation,allowshrinking class * implements com.google.gson.JsonDeserializer
# kotlin metadata for coroutines / reflection used by kotlinx
-keepclassmembers class kotlin.Metadata { *; }
-dontwarn org.slf4j.**
-dontwarn java.awt.**
-dontwarn javax.annotation.**
