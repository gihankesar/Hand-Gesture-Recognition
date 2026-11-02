def main():
    spacecraft = {"name": "voyeger 1", "distance": "163"}
    spacecraft.update({"orbit":"Sun"})
    print(create_report(spacecraft))
def create_report(spacecraft):
    return f"""
    ==========-REPORT-==========

    Name: {spacecraft.get("name","Unknown")}
    Distance: {spacecraft.get("distance", "Unknown")}
    Orbit: {spacecraft.get("orbit", "Unkown")}
    ============================
    """

main()