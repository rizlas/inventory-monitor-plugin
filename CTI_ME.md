### **Jak datový model funguje**
1. **Contractor**
   - Reprezentuje externí společnost nebo jednotlivce, kteří poskytují služby nebo komponenty.
   - Je propojen s více smlouvami (`Contract`).

2. **Contract**
   - Reprezentuje obchodní dohodu, například nákup komponent nebo služeb.
   - Může obsahovat:
     - Více faktur (`Invoice`) pro účely fakturace.
     - Podřízené smlouvy (`Contract`) pro hierarchické řízení smluv.
     - Komponenty (`Component`) spojené se smlouvou.
     - Služby (`ComponentService`) poskytované v rámci smlouvy.

3. **Invoice**
   - Je propojen s konkrétní smlouvou a reprezentuje detaily fakturace.
   - Obsahuje informace o fakturačních obdobích a projektové fakturaci.

4. **Component**
   - Reprezentuje fyzické nebo logické komponenty zapojené do projektu.
   - Obsahuje detaily jako sériové číslo, cenu, dodavatele, záruku a propojení s projektem.
   - Je propojen se službami (`ComponentService`) a zařízeními, lokalitami, místy nebo položkami inventáře.

5. **ComponentService**
   - Reprezentuje služby poskytované pro komponentu, jako je údržba nebo předplatné.
   - Obsahuje informace o období služby, parametrech, cenách a kategoriích služeb.

6. **Probe**
   - Reprezentuje měření nebo sběr dat související se zařízením, lokalitou nebo místem.
   - Obsahuje popisné informace, které identifikují kontext sondy.

---

### **Příklad dat a vztahů**

#### **Scénář**
- Dodavatel jménem **TechCorp** uzavře smlouvu na dodávku komponent a poskytování údržbových služeb pro projekt.
- Projekt zahrnuje nákup směrovačů a přepínačů od **TechCorp**, včetně údržby těchto komponent.
- Smlouva rovněž zahrnuje fakturaci za konkrétní období.

---

#### **Příklad dat**

##### **Contractor**
- **Název**: TechCorp  
- **Společnost**: TechCorp Ltd.  
- **Adresa**: 123 Hlavní ulice, TechCity  
- **Tenant**: Výchozí Tenant  

##### **Contract**
- **Název**: Dodávka síťové infrastruktury  
- **Typ**: Dodávka a údržba  
- **Cena**: 100 000 USD  
- **Podepsáno**: 2025-01-01  
- **Začátek fakturace**: 2025-01-15  
- **Konec fakturace**: 2026-01-15  

##### **Invoice**
- **Název**: Faktura #001  
- **Projekt**: Projekt Alpha  
- **Cena**: 25 000 USD  
- **Začátek fakturace**: 2025-01-15  
- **Konec fakturace**: 2025-02-15  

##### **Component**
- **Sériové číslo**: R12345  
- **Číslo dílu**: RT-5000  
- **Dodavatel**: TechCorp  
- **Cena**: 5 000 USD  
- **Začátek záruky**: 2025-01-15  
- **Konec záruky**: 2028-01-15  
- **Projekt**: Projekt Alpha  

##### **ComponentService**
- **Začátek služby**: 2025-01-15  
- **Konec služby**: 2026-01-15  
- **Parametry služby**: Roční údržba  
- **Cena služby**: 1 000 USD  
- **Kategorie služby**: Údržba  
- **Kategorie služby dodavatele**: TechCorp  

##### **Probe**
- **Čas**: 2025-02-01 10:00:00  
- **Popis zařízení**: Směrovač RT-5000  
- **Popis lokality**: Datové centrum 1  
- **Popis místa**: Rack A1  
- **Část**: Routerový modul  
- **Název**: Kontrola teploty  
- **Sériové číslo**: R12345  
- **Popis**: Měření teploty routeru.  

---

### **Příklad vztahů**
1. **TechCorp** je propojen s kontraktem **Dodávka síťové infrastruktury**.  
2. Tento kontrakt zahrnuje:
   - **Komponentu** (router) se sériovým číslem R12345.  
   - **Službu** roční údržby routeru.  
   - **Fakturu** za fakturační období leden 2025.  
3. **Komponenta** je propojena s:
   - **Lokalitou** (Datové centrum 1).  
   - **Místem** (Rack A1).  
   - **Zařízením** (Směrovač RT-5000).  
4. **Probe** zachycuje provozní data (teplotu) routeru v konkrétním čase.

Tato struktura umožňuje snadné sledování komponent, smluv, faktur a služeb v rámci pluginu NetBox.
